# app/parser.py
import sys
import os
import re
from typing import Dict, Any

# make project root importable if run from app/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_extraction import extract_text
from modules.basic_info_extractor import extract_basic_info
from modules.education_extractor import extract_education
from modules.experience_extractor import extract_experience
from modules.skills_extractor import extract_skills_data
from output_formatter import save_json_for_web, format_console

def parse_resume(path_or_text: str) -> Dict[str, Any]:
    """
    If path_or_text is a path to a file it will extract text; otherwise it's treated as raw text.
    Returns a JSON-serializable dict.
    """
    if os.path.exists(path_or_text):
        text = extract_text(path_or_text)
    else:
        text = path_or_text

    # basic cleaning
    text = (text or "").strip()

    # try to split sections once; pass targeted parts to extractors for better accuracy
    # experience section text
    experience_section = ""
    education_section = ""
    skills_section = ""

    # Try simple header slicing
    lines = text.splitlines()
    text_lower = text.lower()
    # find header indices
    def find_index(names):
        for i, ln in enumerate(lines):
            if any(ln.strip().lower().startswith(n) for n in names):
                return i
        return None

    exp_idx = find_index(["experience", "work experience", "professional experience", "employment"])
    edu_idx = find_index(["education", "academic", "qualification", "qualifications"])
    skills_idx = find_index(["skills", "key skills", "technical skills"])

    # compute slices with safe defaults
    if exp_idx is not None:
        start = exp_idx + 1
        end = edu_idx if (edu_idx and edu_idx > start) else (skills_idx if (skills_idx and skills_idx > start) else len(lines))
        experience_section = "\n".join(lines[start:end]).strip()
    if edu_idx is not None:
        start = edu_idx + 1
        end = skills_idx if (skills_idx and skills_idx > start) else (exp_idx if (exp_idx and exp_idx > start) else len(lines))
        education_section = "\n".join(lines[start:end]).strip()
    if skills_idx is not None:
        start = skills_idx + 1
        end = exp_idx if (exp_idx and exp_idx > start) else (edu_idx if (edu_idx and edu_idx > start) else len(lines))
        skills_section = "\n".join(lines[start:end]).strip()

    # If sections are empty, pass full text to extractors as fallback
    personal_info = extract_basic_info(text)
    education = extract_education(education_section or text)
    experience = extract_experience(experience_section or text)
    skills_data = extract_skills_data(skills_section or text)

    return {
        "personal_info": personal_info,
        "education": education,
        "experience": experience,
        "skills": skills_data.get("skills", []),
        "certifications": skills_data.get("certifications", []),
        "awards": skills_data.get("awards", [])
    }


if __name__ == "__main__":
    sample_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "1.pdf"))
    print(f"Looking for sample PDF at: {sample_pdf}")
    if not os.path.exists(sample_pdf):
        raise FileNotFoundError(sample_pdf)
    parsed = parse_resume(sample_pdf)
    # print(parsed)
    save_json_for_web(parsed,'./output.json')
    print(format_console(parsed))