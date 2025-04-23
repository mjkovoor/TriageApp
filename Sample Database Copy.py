import pandas as pd
import random

# Define specialties and sample symptoms
specialty_symptoms = {
    "Cardiology": [
        "Chest pain on exertion", "Shortness of breath when lying flat", "Irregular heartbeat",
        "Swelling in the legs", "Tightness in the chest after exercise", "Palpitations and dizziness",
        "Fatigue with mild activity", "Pain radiating to left arm", "Rapid heartbeat at rest",
        "Shortness of breath and chest discomfort"
    ],
    "Pulmonology": [
        "Chronic cough with mucus", "Wheezing and breathlessness", "Chest tightness, especially at night",
        "Coughing up blood", "Shortness of breath after walking", "Frequent respiratory infections",
        "Persistent dry cough", "Breathing difficulty in cold air", "Noisy breathing and coughing",
        "Sudden shortness of breath"
    ],
    "Neurology": [
        "Frequent headaches and light sensitivity", "Numbness in hands or feet", "Sudden confusion and disorientation",
        "Difficulty speaking or slurred speech", "Loss of balance and coordination", "Tremors in hands",
        "Seizures without warning", "Sharp shooting pain down the spine", "Visual disturbances and dizziness",
        "Weakness on one side of the body"
    ],
    "Dermatology": [
        "Red, itchy patches on skin", "Dry, flaky scalp", "Sudden appearance of moles",
        "Persistent acne breakouts", "Painful blisters on hands", "Rash that doesn’t go away",
        "Discolored spots on the skin", "Itching and peeling between toes", "Scaly skin on elbows",
        "Hives and swelling after eating certain foods"
    ],
    "Gastroenterology": [
        "Abdominal cramps after meals", "Nausea and vomiting", "Bloating and excessive gas",
        "Change in bowel habits", "Blood in stool", "Persistent heartburn",
        "Loss of appetite and weight loss", "Difficulty swallowing", "Chronic constipation",
        "Upper abdominal pain after eating"
    ],
    "Endocrinology": [
        "Fatigue and increased thirst", "Unexplained weight gain", "Heat intolerance and sweating",
        "Hair thinning and brittle nails", "Menstrual irregularities", "Mood swings and anxiety",
        "Cold intolerance and weight gain", "Excessive hunger despite eating", "Dry skin and constipation",
        "Frequent urination and blurry vision"
    ],
    "Psychiatry": [
        "Lack of interest in daily activities", "Persistent sadness and crying spells", "Sudden mood changes",
        "Trouble concentrating and remembering", "Anxiety in social situations", "Sleep disturbances and nightmares",
        "Irritability and anger outbursts", "Feeling worthless and hopeless", "Obsessive thoughts and compulsive behaviors",
        "Paranoia and hallucinations"
    ],
    "Orthopedics": [
        "Joint pain and stiffness in the morning", "Back pain after lifting heavy objects", "Swelling in the ankle after injury",
        "Pain in shoulder with movement", "Cracking sounds in joints", "Limited range of motion in knee",
        "Bone pain at night", "Difficulty walking after a fall", "Hip pain when climbing stairs",
        "Numbness in fingers after repetitive motion"
    ],
    "OB/GYN": [
        "Irregular menstrual cycles", "Lower abdominal cramps", "Unusual vaginal discharge",
        "Pain during intercourse", "Heavy bleeding during periods", "Missed periods and nausea",
        "Back pain during pregnancy", "Swelling in legs during pregnancy", "Frequent urination and pelvic pressure",
        "Breast tenderness and mood swings"
    ],
    "Urology": [
        "Painful urination and burning sensation", "Blood in urine", "Frequent nighttime urination",
        "Urgent need to urinate with little output", "Difficulty starting urination", "Weak urine stream",
        "Pelvic pain and cloudy urine", "Leakage of urine during sneezing", "Discomfort in lower abdomen",
        "Recurrent urinary tract infections"
    ]
}

# Generate dataset
data = []
for specialty, symptoms in specialty_symptoms.items():
    for symptom in symptoms:
        data.append({"symptom": symptom, "specialty": specialty})

# Shuffle and create DataFrame
random.shuffle(data)
df = pd.DataFrame(data)

# Save to files
df.to_csv("synthetic_triage_data.csv", index=False)
df.to_json("synthetic_triage_data.json", orient="records", indent=2)
