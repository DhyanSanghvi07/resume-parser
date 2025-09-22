import os
import re
import logging
import yaml
import json
import spacy
from typing import List, Dict, Any

# ==========================
# Setup & Config
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f) or {}
else:
    CONFIG = {}

logging.basicConfig(level=logging.INFO)

# Load spaCy with fallback
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("SpaCy model 'en_core_web_sm' not found. University extraction may be limited.")
    nlp = None

# ==========================
# Regex Patterns
# ==========================
DEGREE_KEYWORDS = [
    r"\bDiploma\b",r"\bMBA\b", r"\bB\.?Tech\b", r"\bM\.?Tech\b", r"\bB\.?E\b", r"\bM\.?E\b",
    r"\bB\.?Sc\b", r"\bM\.?Sc\b", r"\bB\.?Com\b", r"\bM\.?Com\b", r"\bBachelor\b",
    r"\bMaster\b", r"\bPh\.?D\b", r"\bHSC\b", r"\bSSC\b", r"\bHigh School\b"
]
DEGREE_PATTERN = re.compile("|".join(DEGREE_KEYWORDS), re.IGNORECASE)

YEAR_PATTERN = re.compile(r"(?:(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}|(?:19|20)\d{2})", re.IGNORECASE)

POSSIBLE_UNI = re.compile(
    r"\b([A-Z][A-Za-z&.\-]{1,}(?:\s(?:University|College|Institute|School|Academy|Polytechnic|Tech)\b)?"
    r"(?:\s[A-Z][A-Za-z&.\-]{1,}){0,5})\b"
)

GRADE_PATTERN = re.compile(
    r'(?:\d{1,2}\.\d{1,2}|(?:GPA|CGPA|Percentage)\s*:?[\s\d\.]+)', re.IGNORECASE
)

EDUCATION_HEADERS = ["education", "academic", "qualifications", "background"]

# ==========================
# Helpers
# ==========================
def _clean_year_string(year_str: str) -> str:
    """Standardize year strings."""
    if not year_str:
        return "N/A"
    year_str = year_str.replace("–", "-").strip()
    if re.fullmatch(r"\d{4}", year_str):
        return year_str
    if re.fullmatch(r"\d{4}\s*-\s*\d{4}", year_str):
        return year_str
    if re.fullmatch(r"\d{4}\s*-\s*(?:Present|Now|Ongoing)", year_str, re.IGNORECASE):
        return year_str.replace("Present", "Now").replace("Ongoing", "Now")
    return "N/A"


def extract_education_section(text: str):
    """Return only education section lines if headers found, else all lines."""
    lines = text.splitlines()
    start, end = -1, len(lines)

    for idx, line in enumerate(lines):
        if any(h in line.lower() for h in EDUCATION_HEADERS):
            start = idx
            break

    if start == -1:
        return lines  # fallback: return everything

    for idx in range(start + 1, len(lines)):
        if lines[idx].strip() and lines[idx] == lines[idx].upper() and len(lines[idx].split()) <= 4:
            end = idx
            break
    return lines[start:end]


def parse_ed_buffer(buffer: List[str]) -> List[Dict[str, Any]]:
    """Parse buffered lines into structured education entry."""
    joined = " ".join(buffer)

    degree_match = DEGREE_PATTERN.search(joined)
    degree = degree_match.group() if degree_match else "N/A"

    year_match = YEAR_PATTERN.search(joined)
    years = _clean_year_string(year_match.group()) if year_match else "N/A"

    grade_match = GRADE_PATTERN.search(joined)
    grade = grade_match.group() if grade_match else "N/A"

    uni = "N/A"
    if nlp:
        try:
            doc = nlp(joined)
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if orgs:
                uni = orgs[0]
        except Exception as e:
            logging.error(f"SpaCy NER failed: {e}")

    if uni == "N/A":
        possible_unis = POSSIBLE_UNI.findall(joined)
        if possible_unis:
            uni = max(possible_unis, key=len).strip()

    return [{
        "degree": degree,
        "university": uni,
        "years": years,
        "grade": grade
    }]

# ==========================
# Main Function
# ==========================
def extract_education(text: str) -> List[Dict[str, Any]]:
    """
    Extract education entries from resume text.
    Returns: list of dicts {degree, university, years, grade}
    """
    lines = extract_education_section(text)
    entries, buffer = [], []

    for line in lines:
        if DEGREE_PATTERN.search(line):
            if buffer:
                entries.extend(parse_ed_buffer(buffer))
                buffer = []
        buffer.append(line)

    if buffer:
        entries.extend(parse_ed_buffer(buffer))

    # Optional: fallback to LLM if nothing found
    if not entries and (CONFIG.get("GROQ_API_KEY") or CONFIG.get("LLM_API_KEY")):
        try:
            from langchain_groq import ChatGroq
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatGroq(api_key=CONFIG.get("GROQ_API_KEY") or CONFIG.get("LLM_API_KEY"),
                           model="llama3-70b-8192")

            prompt = ChatPromptTemplate.from_template(
                """
                Extract education entries from this resume.
                Return JSON array:
                [
                  {"degree": "...", "university": "...", "years": "YYYY - YYYY", "grade": "..."}
                ]
                Use "N/A" if not found.
                Text:
                {text}
                """
            )
            chain = prompt | llm
            response = chain.invoke({"text": text})
            json_start = response.content.find("[")
            json_end = response.content.rfind("]")

            if json_start != -1 and json_end != -1:
                entries = json.loads(response.content[json_start:json_end + 1])

        except Exception as e:
            logging.error(f"LLM fallback failed: {e}")

    return entries