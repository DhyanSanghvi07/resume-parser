import os
import json
import yaml
import re
import spacy
import docx2txt
from typing import List, Dict
from pdfminer.high_level import extract_text as extract_text_from_pdf
from spacy.matcher import PhraseMatcher

try:
    from groq import Groq  # ✅ Optional Groq SDK
except ImportError:
    Groq = None


# ---------------------------
# Load Config
# ---------------------------
CONFIG = {}
if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)

GROQ_API_KEY = CONFIG.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if (Groq and GROQ_API_KEY) else None

# ---------------------------
# Load SpaCy and Skills DB
# ---------------------------
nlp = spacy.load("en_core_web_sm")

# Load skills from ../nlp/skills.json
SKILLS_DB = []
skills_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "../nlp/skills.json"))
if os.path.exists(skills_file):
    with open(skills_file, "r", encoding="utf-8") as f:
        SKILLS_DB = json.load(f)

# Prepare matcher only once
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in SKILLS_DB]
if patterns:
    matcher.add("SKILLS", patterns)


# ---------------------------
def extract_awards_section(text: str) -> List[str]:
    lines = text.splitlines()
    awards = []
    block = ""
    capture = False
    section_keywords = ['skills', 'education', 'experience', 'languages', 'projects', 'certifications']

    for line in lines:
        line_strip = line.strip()
        line_lower = line_strip.lower()

        if any(kw in line_lower for kw in [
            'awards', 'recognition', 'accomplishments', 'achievements', 'honors',
            'prizes', 'distinctions', 'accolades', 'awards and honors'
        ]):
            capture = True
            continue

        if capture and (
            any(re.fullmatch(rf"{kw}[ .:]*", line_lower) for kw in section_keywords)
            or re.match(r"^[A-Z][A-Z\s]{2,}$", line_strip)
        ):
            if block.strip():
                awards.append(block.strip())
            break

        if capture:
            if not line_strip or len(line_strip) <= 2:
                if block.strip():
                    awards.append(block.strip())
                    block = ""
            else:
                block += (" " if block else "") + line_strip

    if block.strip():
        awards.append(block.strip())

    return [a for a in awards if re.search(r"[a-zA-Z]", a) and len(a) > 10]


# ---------------------------
def extract_skills_certifications_spacy(text: str) -> Dict[str, List[str]]:
    doc = nlp(text.lower())
    matches = matcher(doc)
    found_skills = sorted(set(doc[start:end].text for _, start, end in matches))

    certifications = [
        sent.text.strip()
        for sent in doc.sents
        if re.search(r"(certified|certificate|completion|credential|awarded)", sent.text.lower())
    ]

    return {
        "skills": found_skills,
        "certifications": certifications
    }


# ---------------------------
def extract_json_block(text: str) -> dict:
    try:
        json_start = text.find('{')
        json_text = text[json_start:]
        return json.loads(json_text)
    except Exception:
        raise ValueError("No valid JSON block found in LLM response.")


# ---------------------------
def extract_skills_certifications_llm(text: str) -> Dict[str, List[str]]:
    if not client:
        return {"skills": [], "certifications": [], "awards": []}

    prompt = f"""
    You are a smart resume analyzer.

    From the resume text below, extract:
    {{
      "skills": [...],
      "certifications": [...],
      "awards": [...]
    }}
    Resume:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        parsed = extract_json_block(response.choices[0].message.content)
        return {
            "skills": parsed.get("skills", []),
            "certifications": parsed.get("certifications", []),
            "awards": parsed.get("awards", [])
        }
    except Exception:
        return {"skills": [], "certifications": [], "awards": []}


# ---------------------------
def extract_skills_data(resume_text: str) -> Dict[str, List[str]]:
    result_spacy = extract_skills_certifications_spacy(resume_text)
    result_spacy["awards"] = extract_awards_section(resume_text)

    if not any(result_spacy.values()):
        return extract_skills_certifications_llm(resume_text)

    return result_spacy