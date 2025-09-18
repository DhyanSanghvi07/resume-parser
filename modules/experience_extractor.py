import re
from typing import List, Dict
import spacy

# load spaCy English model
nlp = spacy.load("en_core_web_sm")

SECTION_HEADERS = re.compile(r'^(EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT)\b', re.I)


def _section_text(text: str, header_names=None) -> str:
    """Extract experience section using header anchors. Return section or full text fallback."""
    header_names = header_names or ["experience", "work experience", "professional experience", "employment"]
    lines = text.splitlines()
    start_idx = None
    end_idx = None
    for i, ln in enumerate(lines):
        if any(ln.strip().lower().startswith(h) for h in header_names):
            start_idx = i + 1
            break
    if start_idx is None:
        return text  # fallback to whole text
    # find next major header to stop
    for j in range(start_idx, len(lines)):
        if re.match(r'^[A-Z][A-Z\s]{2,}$', lines[j].strip()):
            end_idx = j
            break
    if end_idx is None:
        end_idx = len(lines)
    return "\n".join(lines[start_idx:end_idx]).strip()


def _merge_bullets(section_text: str) -> List[str]:
    bullets = []
    current = ""
    for line in section_text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        if ln.startswith(("•", "-", "*")) or re.match(r'^\d+\.', ln):
            if current:
                bullets.append(current.strip())
            current = re.sub(r'^[•\-\*\d\.\)\s]+', '', ln)
        else:
            # continuation of previous bullet
            current = (current + " " + ln).strip()
    if current:
        bullets.append(current.strip())
    return bullets


def extract_experience(text: str) -> List[Dict]:
    """
    Returns list of experiences:
    [{'company':..., 'role':..., 'duration':..., 'responsibilities':[...]}]
    """
    section = _section_text(text)
    bullets = _merge_bullets(section)
    results = []

    for b in bullets:
        # --- Duration extraction (dates or years) ---
        duration_match = re.search(
            r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]\s+\d{4}(\s[-–]\s*(Present|\d{4}))?)',
            b, re.I
        )
        duration = duration_match.group(0) if duration_match else "Not Found"

        # --- spaCy NER for organizations ---
        doc = nlp(b)
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        company = orgs[0] if orgs else "Not Found"

        # --- Role detection (common job titles) ---
        role_match = re.search(
            r'\b(Teacher|Engineer|Developer|Manager|Analyst|Intern|Assistant|Lead|Designer|Consultant)\b',
            b, re.I
        )
        role = role_match.group(0) if role_match else "Not Found"

        # --- Responsibilities ---
        # Split on punctuation and semicolons, keep meaningful parts
        responsibilities = re.split(r'[.;•]', b)
        responsibilities = [r.strip() for r in responsibilities if r.strip() and len(r.strip()) > 8][:6]

        results.append({
            "company": company,
            "role": role,
            "duration": duration,
            "responsibilities": responsibilities
        })

    if not results:
        # fallback if nothing extracted
        return [{
            "company": "Not Found",
            "role": "Not Found",
            "duration": "Not Found",
            "responsibilities": []
        }]
    return results
