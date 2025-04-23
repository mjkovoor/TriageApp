import openai
import requests
import gradio as gr
import json
import os
from dotenv import load_dotenv

load_dotenv()
# Set your OpenAI API key (use env var in real use!)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Ollama URL configuration and model
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

# List of specialties
specialties = [
    "Cardiology", "Pulmonology", "Neurology", "Dermatology", "Gastroenterology",
    "Endocrinology", "Psychiatry", "Orthopedics", "OB/GYN", "Urology"
]

# System + user prompt template
def classify_symptom(symptom_text):
    system_prompt = "You are a helpful medical triage assistant."
    
    prompt = f"""
    Based on the following patient symptoms, identify the most appropriate medical specialty from this list:
    {", ".join(specialties)}.

    Symptoms: "{symptom_text}"

    Only return the specialty name.
    """
    response = ask_model(prompt)
    return f"🔎 Suggested Specialty: **{response}**"

    

def ask_model(prompt):

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical triage asssistant."},
                {"role": "user", "content": prompt}],
                temperature=0.2,
                timeout=10 #short timeout to swap to Ollama if OpenAI not working
        )
            
        specialty = response['choices'][0]['message']['content'].strip()
        return specialty
        
    
    except Exception as e:
        print(f"⚠️ Cloud model failed, falling back to local. Reason: {e}")

        # Fallback to local Ollama model
        try:
            ollama_response = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt},
                stream=True
            )
            response_text = ""
            for line in ollama_response.iter_lines():
                if line:
                    try:
                        chunk = line.decode("utf-8")
                        json_chunk = json.loads(chunk)
                        response_text += json_chunk.get("response", "")
                    except Exception as parse_err:
                        print(f"⚠️ Failed to parse chunk: {parse_err}")
            return response_text.strip() or "No response from local model"
        #     result = ollama_response.json()
        #     return result.get("response", "No response from local model")
        except Exception as ex:
            return f"❌ Both cloud and local models failed: {ex}"

# Gradio interface
demo = gr.Interface(
    fn=classify_symptom,
    inputs=gr.Textbox(lines=4, placeholder="Enter patient symptoms here..."),
    outputs="markdown",
    title="AI Medical Triage Assistant",
    description="Enter a patient's symptoms and get a suggested medical specialty."
)

# Launch app
if __name__ == "__main__":
    demo.launch()
