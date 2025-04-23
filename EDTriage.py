import openai
import requests
import gradio as gr
import json
from Bio import Entrez
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
Entrez.email = "mjkovoor@users.noreply.github.com"

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

'''
This method will fetch pubmed articles based on the search query and compile abstracts.
Future goals: integrate these pubmed articles with the output to make data-driven recommendations
'''
def fetch_pubmed_abstracts(query, max_results=10):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    ids = record["IdList"]

    if not ids:
        print("❗ No PubMed IDs found for query:", query)
    else:
        print(f"✅ Found {len(ids)} IDs for query: {query}")
        print("PMIDs:", ids)

    abstracts = []
    for uid in ids:
        fetch_handle = Entrez.efetch(db="pubmed", id=uid, rettype="abstract", retmode="text")
        abstract_text = fetch_handle.read()
        if abstract_text.strip():
            abstracts.append(abstract_text)
    return abstracts

'''
This does a similarity search based on the pubmed IDs of the abstracts found
'''
def embed_and_search(query, pmid_abstract_pairs, k=3):
    documents = []
    for pmid, abstract in pmid_abstract_pairs:
        chunks = text_splitter.split_text(abstract)
        for chunk in chunks:
            # Store PMID in metadata for later reference
            documents.append(Document(page_content=chunk, metadata={"pmid": pmid}))
    db = FAISS.from_documents(documents, embedding_model)
    return db.similarity_search(query, k=k)


'''
This method takes in the query results and uses a search to comb pubmed for relevant articles based on key information from the case
'''
def triage_assistant(symptoms, vitals, age, weight, pmh, last_known_well, exam_findings):
    search_query = f"{symptoms} {pmh}".strip()
    pmid_abstracts = fetch_pubmed_abstracts(search_query)

    if not pmid_abstracts:
        context = "❗ No relevant literature found on PubMed."
    else:
        results = embed_and_search(search_query, pmid_abstracts)
        context_chunks = []
        for doc in results:
            pmid = doc.metadata.get("pmid", "unknown")
            chunk = doc.page_content.strip()
            context_chunks.append(f"{chunk}\n[PMID: {pmid}]")
        context = "\n\n".join(context_chunks)

    prompt = f"""
You are an emergency triage AI. Given the following patient info, return:

1. Top 3 differentials (w/ % likelihood)
2. Immediate stabilization steps
3. Meds/fluids + dosages
4. Consults
5. Labs/Imaging required
6. Evidence-based justification (landmark studies, guidelines, or standard practices). Cite PMIDs when possible.

Patient details:
- Symptoms: {symptoms}
- Vitals: {vitals}
- Age: {age}
- Weight: {weight}
- Past Medical History: {pmh}
- Last Known Well: {last_known_well}
- Physical Exam Findings: {exam_findings}

Here are relevant PubMed Abstracts:
{context}

Be concise, clear, and structured in your response.
    """

    print("🧾 Prompt preview:\n", prompt[:1000], "\n...")
    return ask_model(prompt)


'''
This will use OpenAI to generate a response if available. Otherwise it'll fall back to Ollama's mistral model. 
Future goal: fall back to meditron and integrating a local NLP
'''
def ask_model(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful emergency medicine AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            timeout=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Cloud model failed, falling back to local. Reason: {e}")
        try:
            ollama_response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "stream": True,
                    "prompt": prompt
                },
                stream=True
            )
            response_text = ""
            for line in ollama_response.iter_lines():
                if line:
                    try:
                        decoded = json.loads(line.decode("utf-8"))
                        response_text += decoded.get("response", "")
                    except json.JSONDecodeError:
                        continue
            return response_text.strip() or "❌ Empty response from local model"
        except Exception as ollama_err:
            return f"❌ Both cloud and local models failed: {ollama_err}"

demo = gr.Interface(
    fn=triage_assistant,
    inputs=[
        gr.Textbox(label="Symptoms", placeholder="e.g. chest pain, shortness of breath"),
        gr.Textbox(label="Vitals", placeholder="e.g. HR 120, BP 85/60, RR 28, Temp 101°F"),
        gr.Textbox(label="Age", placeholder="e.g. 72"),
        gr.Textbox(label="Weight (kg)", placeholder="e.g. 65"),
        gr.Textbox(label="Past Medical History", placeholder="e.g. CAD, diabetes"),
        gr.Textbox(label="Last Known Well", placeholder="e.g. 2 hours ago"),
        gr.Textbox(label="Physical Exam Findings", placeholder="e.g. crackles in lungs, cool extremities"),
    ],
    outputs="markdown",
    title="🩺 AI Emergency Triage Assistant",
    description="Provide optional patient details to receive suggested differentials, interventions, and consults."
)

if __name__ == "__main__":
    demo.launch()
