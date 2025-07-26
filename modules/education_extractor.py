import re
import spacy
import os
import yaml
import json
from typing import List, Dict, Set, Tuple   
from pdfminer.high_level import extract_text as extract_text_from_pdf
import docx2txt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

nlp = spacy.load("en_core_web_sm")

with open("config.yaml") as f:
    api_key = yaml.safe_load(f)["GROQ_API_KEY"]

llm = ChatGroq(
    api_key=api_key,
    model="llama3-70b-8192"
)

DEGREE_KEYWORDS = [
    r"\bDiploma\b", r"\bB\.?Tech\b", r"\bM\.?Tech\b", r"\bB\.?E\b", r"\bM\.?E\b",
    r"\bB\.?Sc\b", r"\bM\.?Sc\b", r"\bB\.?Com\b", r"\bM\.?Com\b",
    r"\bBachelor\b", r"\bMaster\b", r"\bPh\.?D\b", r"\bHSC\b", r"\bSSC\b", r"\bHigh School\b"
]
DEGREE_PATTERN = re.compile(r"|".join(DEGREE_KEYWORDS), re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(Expected\s*)?(19|20)\d{2}", re.IGNORECASE)

UNIVERSITY_KEYWORDS = [
    "college", "university", "institute", "school", "vesp", "junior",
    "mit", "vjti", "iit", "iiit", "nit", "bits", "sit", "vit"
]
POSSIBLE_UNIVERSITY_PATTERN = re.compile(
    r"\b([A-Z][A-Za-z&.\-]{1,}(?:\s[A-Z][A-Za-z&.\-]{1,}){0,4})\b"
)

def extract_education_fallback(text: str) -> List[Dict]:
    print("Using fallback rule-based extraction...")
    lines = text.split('\n')
    education_entries = []
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
                if any(keyword in name.lower() for keyword in UNIVERSITY_KEYWORDS):
                    clean = re.sub(r"^(Diploma in|B\.?Tech|M\.?Tech|Bachelor|Master|Ph\.?D|HSC|SSC|High School)\s*[-:]\s", "", name, flags=re.IGNORECASE)
                    universities.append(clean.strip(" -:"))

            education_entries.append({
                "degree": ", ".join(degrees),
                "university": ", ".join(set(universities)) if universities else "Not Found",
                "years": year
            })
            buffer = ""

    return education_entries

# LLM-based extraction
def extract_education_with_llm(text: str) -> List[Dict]:
    print("Using LLM for extraction...")
    try:
        prompt = ChatPromptTemplate.from_template(
            """
            You are an intelligent education extractor. From the following resume text:
            '''
            {text}
            '''
            Extract only the education section. Return strictly a JSON array of dictionaries in this format:
            [{{"degree": "B.Tech", "university": "MIT", "years": "2020"}}]
            Do not include any explanation or extra text.
            """
        )
        chain = prompt | llm
        response = chain.invoke({"text": text})
        return json.loads(response.content.strip())
    except Exception as e:
        print("LLM extraction failed, falling back to rule-based method. Reason:", e)
        return None

def extract_education_as_tuples(text: str) -> Set[Tuple[str, str, str]]:
    """
    Wrapper that keeps your existing logic intact but returns a set of
    (degree, university, years) tuples, similar to your Code 2 output.
    """
    llm_result = extract_education_with_llm(text)
    results = llm_result if llm_result else extract_education_fallback(text)

    out: Set[Tuple[str, str, str]] = set()
    for item in results:
        out.add((
            item.get("degree", "Not Found"),
            item.get("university", "Not Found"),
            item.get("years", "Not Found")
        ))
    return out
# ----------------------------------------------------
