import os
import re
import json
import logging
import yaml
from typing import List, Dict
import spacy
from spacy.matcher import PhraseMatcher

# ----------------- CONFIG -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f) or {}
else:
    CONFIG = {}

logging.basicConfig(level=logging.INFO)

# ----------------- SPACY -----------------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("SpaCy model 'en_core_web_sm' not found. Skills extraction may be limited.")
    nlp = None

# ----------------- SKILLS DB -----------------
skills_path = os.path.normpath(os.path.join(BASE_DIR, "..", "nlp", "skills.json"))
if os.path.exists(skills_path):
    with open(skills_path, "r", encoding="utf-8") as fh:
        SKILLS_DB = json.load(fh)
else:
    SKILLS_DB = []

matcher = PhraseMatcher(nlp.vocab, attr="LOWER") if nlp else None
if SKILLS_DB and matcher:
    patterns = [nlp.make_doc(s) for s in SKILLS_DB]
    matcher.add("SKILLS", patterns)

# ----------------- UTILITIES -----------------
def dedup_preserve_order(items: List[str]) -> List[str]:
    seen, out = set(), []
    for it in items:
        key = it.lower()
        if key not in seen and it:
            seen.add(key)
            out.append(it.strip())
    return out

def _simple_substring_match(text: str, skills_list) -> List[str]:
    text_l = text.lower()
    found = set()
    for s in skills_list:
        key = s.lower()
        if len(key) < 2:
            continue
        if key in text_l:
            found.add(s)
        else:
            parts = [p for p in re.split(r'\W+', key) if p]
            if len(parts) > 1:
                hits = sum(1 for p in parts if p in text_l)
                if hits >= max(1, len(parts) - 1):
                    found.add(s)
    return sorted(found)

def normalize_heading(text: str) -> str:
    """Normalize headings by removing spaces, special chars, and lowercasing."""
    return re.sub(r'[^a-z0-9]', '', text.lower())

# ----------------- GENERIC SECTION EXTRACTION -----------------
def extract_section(resume_text: str, headings: List[str], stop_headings: List[str] = None) -> List[str]:
    """
    Extract lines under a heading until the next heading is found.
    """
    if stop_headings is None:
        stop_headings = [
            'experience', 'skills', 'technicalskills', 'projects',
            'awards', 'certificates', 'certificate', 'education'
        ]
        # ⛔ Removed 'achievements' and 'certifications' so they won't block capture

    capture = False
    lines_out = []

    normalized_headings = [normalize_heading(h) for h in headings]
    normalized_stops = [normalize_heading(h) for h in stop_headings]

    for line in resume_text.splitlines():
        l = line.strip()
        if not l:
            continue
        norm = normalize_heading(l)

        if norm in normalized_headings:  # start capturing
            capture = True
            continue

        if capture and norm in normalized_stops:
            break

        if capture:
            lines_out.append(l)

    return dedup_preserve_order(lines_out)

# ----------------- CERTIFICATIONS -----------------
def extract_certifications(resume_text: str) -> List[str]:
    cert_headings = ['certificate', 'certificates', 'certification', 'certifications']
    return extract_section(resume_text, cert_headings)

# ----------------- AWARDS -----------------
def extract_awards(resume_text: str) -> List[str]:
    award_headings = ['award', 'awards', 'achievement', 'achievements']
    return extract_section(resume_text, award_headings)

# ----------------- TECHNICAL SKILLS -----------------
def extract_technical_skills(resume_text: str) -> List[str]:
    tech_headings = ['technical skills', 'skills']
    return extract_section(resume_text, tech_headings)

# ----------------- SKILLS DATA -----------------
def extract_skills_data(resume_text: str) -> Dict[str, List[str]]:
    if not resume_text:
        return {"skills": [], "certifications": [], "awards": []}

    # Skills extraction from SpaCy/DB
    skills = []
    if nlp and matcher:
        doc = nlp(resume_text)
        matches = matcher(doc) if SKILLS_DB else []
        skills = sorted({doc[start:end].text.lower() for _, start, end in matches})
    if not skills and SKILLS_DB:
        skills = _simple_substring_match(resume_text, SKILLS_DB)

    # Extract explicit Technical Skills section
    tech_skills = extract_technical_skills(resume_text)

    # Merge + dedup
    all_skills = dedup_preserve_order(skills + tech_skills)

    # Certifications extraction
    certifications = extract_certifications(resume_text)

    # Awards extraction
    awards = extract_awards(resume_text)

    return {"skills": all_skills, "certifications": certifications, "awards":awards}