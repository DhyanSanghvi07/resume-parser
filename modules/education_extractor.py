import os
import re
from typing import List, Dict
import spacy
import yaml
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load config from modules/config.yaml if present (safe)
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f) or {}
else:
    CONFIG = {}

nlp = spacy.load("en_core_web_sm")

DEGREE_KEYWORDS = [
    r"\bDiploma\b", r"\bB\.?Tech\b", r"\bM\.?Tech\b", r"\bB\.?E\b", r"\bM\.?E\b",
    r"\bB\.?Sc\b", r"\bM\.?Sc\b", r"\bB\.?Com\b", r"\bM\.?Com\b", r"\bBachelor\b",
    r"\bMaster\b", r"\bPh\.?D\b", r"\bHSC\b", r"\bSSC\b", r"\bHigh School\b", r"\bCertificate\b"
]
DEGREE_PATTERN = re.compile("|".join(DEGREE_KEYWORDS), re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(19|20)\d{2}(?:\s*[-–]\s*(19|20)\d{2})?", re.IGNORECASE)

POSSIBLE_UNI = re.compile(r"\b([A-Z][A-Za-z&.\-]{1,}(?:\s[A-Z][A-Za-z&.\-]{1,}){0,5})\b")


def extract_education_fallback(text: str) -> List[Dict]:
    """Return list of education dicts: {'degree', 'university', 'years'}"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    entries = []
    buffer = ""
    for line in lines:
        buffer = (buffer + " " + line).strip()
        if DEGREE_PATTERN.search(buffer):
            degree_match = DEGREE_PATTERN.search(buffer)
            degree = degree_match.group(0).strip()
            year_match = YEAR_PATTERN.search(buffer)
            years = year_match.group(0) if year_match else "Not Found"

            # NER attempt for ORG
            doc = nlp(buffer)
            orgs = [ent.text for ent in doc.ents if ent.label_ in ("ORG", "GPE")]
            possible_unis = POSSIBLE_UNI.findall(buffer)
            uni = "Not Found"
            # prefer orgs from NER
            if orgs:
                uni = orgs[0]
            elif possible_unis:
                # choose a candidate containing university/college/institute keywords - else first
                for p in possible_unis:
                    if any(k in p.lower() for k in ("university", "college", "institute", "school")):
                        uni = p
                        break
                if uni == "Not Found":
                    uni = possible_unis[0]

            entries.append({
                "degree": degree,
                "university": uni,
                "years": years
            })
            buffer = ""
    return entries


def extract_education(text: str) -> List[Dict]:
    """
    Unified interface. Returns a list of dicts (degree, university, years).
    If a LLM is configured in CONFIG and available, uses LLM as fallback.
    """
    # first rule-based
    entries = extract_education_fallback(text)
    if entries:
        return entries

    # If empty and LLM is configured, try LLM (guarded)
    groq_key = CONFIG.get("GROQ_API_KEY") or CONFIG.get("LLM_API_KEY")
    if groq_key:
        try:
            # Keep this simple: call a minimal LLM only if available
            from langchain_groq import ChatGroq
            from langchain_core.prompts import ChatPromptTemplate
            llm = ChatGroq(api_key=groq_key, model="llama3-70b-8192")
            prompt = ChatPromptTemplate.from_template(
                """
                Extract education entries from the text below and return a JSON array of
                {"degree": "...", "university":"...", "years":"..."}.
                Text:
                {text}
                """
            )
            chain = prompt | llm
            response = chain.invoke({"text": text})
            return json.loads(response.content.strip())
        except Exception as e:
            print(f"[education_extractor] LLM fallback failed: {e}")
    return entries
