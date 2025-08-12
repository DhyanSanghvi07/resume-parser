import os
import json
import re
from typing import Dict, List
import spacy
from spacy.matcher import PhraseMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load spaCy (light model)
nlp = spacy.load("en_core_web_sm")

# Load skills DB (relative to repo: ../nlp/skills.json)
skills_path = os.path.normpath(os.path.join(BASE_DIR, "..", "nlp", "skills.json"))
if not os.path.exists(skills_path):
    SKILLS_DB = []
else:
    with open(skills_path, "r", encoding="utf-8") as fh:
        SKILLS_DB = json.load(fh)

# Build PhraseMatcher once
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
if SKILLS_DB:
    patterns = [nlp.make_doc(s) for s in SKILLS_DB]
    matcher.add("SKILLS", patterns)


def _simple_substring_match(text: str, skills_list) -> List[str]:
    """Fast substring fallback for short skills."""
    text_l = text.lower()
    found = set()
    for s in skills_list:
        key = s.lower()
        # ignore very short noise (1 char)
        if len(key) < 2:
            continue
        if key in text_l:
            found.add(key)
        else:
            # allow small fuzzy: split multi-word skills and check majority words
            parts = [p for p in re.split(r'\W+', key) if p]
            if len(parts) > 1:
                hits = sum(1 for p in parts if p in text_l)
                if hits >= max(1, len(parts) - 1):
                    found.add(key)
    return sorted(found)


def extract_skills_data(resume_text: str) -> Dict[str, List[str]]:
    """
    Returns:
      {
        "skills": [...],
        "certifications": [...],
        "awards": [...]
      }
    """
    if not resume_text:
        return {"skills": [], "certifications": [], "awards": []}

    doc = nlp(resume_text)
    matches = matcher(doc) if SKILLS_DB else []
    skills = sorted({doc[start:end].text.lower() for _, start, end in matches})

    # Fallback substring matching for cases missed by PhraseMatcher
    if not skills and SKILLS_DB:
        skills = _simple_substring_match(resume_text, SKILLS_DB)

    # Simple certifications detection (heuristic)
    certifications = []
    for sent in doc.sents:
        s = sent.text.strip()
        if re.search(r'\b(certified|certificate|certification|awarded|completion)\b', s, re.I):
            certifications.append(s)

    # awards will be extracted elsewhere; keep minimal here
    awards = []

    return {
        "skills": skills,
        "certifications": certifications,
        "awards": awards
    }
