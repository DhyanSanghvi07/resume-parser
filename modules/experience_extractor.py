import re
import spacy
import os
import yaml
import json
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Load API key
with open("config.yaml") as f:
    api_key = yaml.safe_load(f)["GROQ_API_KEY"]

# Init LLM
llm = ChatGroq(api_key=api_key, model="llama3-70b-8192")

# === Fallback method ===
def extract_experience_fallback(text: str) -> List[Dict]:
    experiences = []
    lines = text.split("\n")
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        buffer += " " + line
        doc = nlp(buffer)
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

        if orgs and dates:
            experiences.append({
                "company": ", ".join(set(orgs)),
                "role": "Not Found",
                "duration": ", ".join(set(dates)),
                "responsibilities": buffer.strip()
            })
            buffer = ""

    return experiences

# === LLM method ===
def extract_experience_with_llm(text: str) -> List[Dict] | None:
    try:
        prompt = ChatPromptTemplate.from_template("""
        You are an intelligent resume parser. From the text below:
        '''
        {text}
        '''
        Extract only the work experience section in this exact JSON format:

        [
        {{
            "company": "Company Name",
            "role": "Job Title",
            "duration": "Start - End",
            "responsibilities": [
            "Short responsibility 1",
            "Short responsibility 2",
            "Short responsibility 3"
            ]
        }}
        ]
        ✱ Guidelines:
        - Summarize long texts into 2–4 short, clear points
        - Do not copy full paragraphs
        - If responsibilities are unclear, infer common duties for that role
        - Output must be only valid JSON, no extra text
        """)

        chain = prompt | llm
        response = chain.invoke({"text": text})

        if response.content.strip().startswith('['):
            return json.loads(response.content.strip())
        return None

    except Exception as e:
        print("LLM error:", e)
        return None

# === Unified interface ===
def extract_experience(text: str) -> List[Dict]:
    llm_result = extract_experience_with_llm(text)

    if isinstance(llm_result, list) and len(llm_result) > 0:
        return llm_result
    elif isinstance(llm_result, list) and len(llm_result) == 0:
        return [{
            "company": "Not Found",
            "role": "Not Found",
            "duration": "Not Found",
            "responsibilities": []
        }]
    elif any(word in text.lower() for word in ["experience", "intern", "worked", "employed", "job", "role"]):
        return extract_experience_fallback(text)
    else:
        return [{
            "company": "Not Found",
            "role": "Not Found",
            "duration": "Not Found",
            "responsibilities": []
        }]