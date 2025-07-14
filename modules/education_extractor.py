import re
import spacy
from typing import Set, Tuple

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Degree patterns
DEGREE_KEYWORDS = [
    r"\bDiploma\b", r"\bB\.?Tech\b", r"\bM\.?Tech\b", r"\bB\.?E\b", r"\bM\.?E\b",
    r"\bB\.?Sc\b", r"\bM\.?Sc\b", r"\bB\.?Com\b", r"\bM\.?Com\b", r"\bBachelor\b",
    r"\bMaster\b", r"\bPh\.?D\b", r"\bHSC\b", r"\bSSC\b", r"\bHigh School\b"
]
DEGREE_PATTERN = re.compile(r"|".join(DEGREE_KEYWORDS), re.IGNORECASE)

# Year pattern
YEAR_PATTERN = re.compile(r"(Expected\s*)?(19|20)\d{2}", re.IGNORECASE)

# University keywords
UNIVERSITY_KEYWORDS = [
    "college", "university", "institute", "school", "vesp", "junior",
    "mit", "vjti", "iit", "iiit", "nit", "bits", "sit", "vit"
]

# Match potential university-like phrases
POSSIBLE_UNIVERSITY_PATTERN = re.compile(
    r"\b([A-Z][A-Za-z&.\-]{1,}(?:\s[A-Z][A-Za-z&.\-]{1,}){0,4})\b"
)

# Extract education tuples: (degree, university, year)
def extract_education(text: str) -> Set[Tuple[str, str, str]]:
    lines = text.split('\n')
    education_entries = set()
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        buffer += " " + line
        buffer = buffer.strip()

        if DEGREE_PATTERN.search(buffer):
            degrees = list(set(DEGREE_PATTERN.findall(buffer)))
            year_match = YEAR_PATTERN.search(buffer)
            year = year_match.group(0).replace("Expected", "").strip() if year_match else "Not Found"

            doc = nlp(buffer)
            nlp_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE"]]
            possible_names = POSSIBLE_UNIVERSITY_PATTERN.findall(buffer)
            all_names = list(set(nlp_entities + possible_names))

            universities = []
            for name in all_names:
                lower = name.lower()
                if any(keyword in lower for keyword in UNIVERSITY_KEYWORDS):
                    clean = re.sub(
                        r"^(Diploma in|B\.?Tech|M\.?Tech|Bachelor|Master|Ph\.?D|HSC|SSC|High School)\s*[-:]\s",
                        "", name, flags=re.IGNORECASE
                    ).strip(" -:")
                    universities.append(clean)

            # If no university found, fallback to matching a keyword directly
            if not universities:
                for keyword in UNIVERSITY_KEYWORDS:
                    if keyword in buffer.lower():
                        universities.append(keyword.upper())
                        break  # Only one fallback added

            universities = list(set(universities)) or ["Not Found"]

            for degree in degrees:
                for university in universities:
                    education_entries.add((degree, university, year))

            buffer = ""

    return education_entries