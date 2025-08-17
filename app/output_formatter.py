# utils/output_formatter.py

import json
import os
from typing import Dict, Any, List

try:
    from fpdf import FPDF  # optional for PDF output
except ImportError:
    FPDF = None

def sanitize_text(text: str) -> str:
    replacements = {
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2026": "...",  # ellipsis
        # Add more replacements as needed
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


def format_console(parsed_data: Dict[str, Any]) -> str:
    """Creates a clean, readable console output of parsed resume data."""
    output_lines = []

    # Personal Info
    output_lines.append("=== PERSONAL INFORMATION ===")
    for key, value in parsed_data.get("personal_info", {}).items():
        output_lines.append(f"{key.capitalize()}: {value}")

    # Education
    output_lines.append("\n=== EDUCATION ===")
    for edu in parsed_data.get("education", []):
        output_lines.append(f"- {edu}")

    # Experience
    output_lines.append("\n=== EXPERIENCE ===")
    for exp in parsed_data.get("experience", []):
        if isinstance(exp, dict):
            exp_str = ", ".join(f"{k.capitalize()}: {v}" for k, v in exp.items())
            output_lines.append(f"- {exp_str}")
        else:
            output_lines.append(f"- {exp}")

    # Skills
    output_lines.append("\n=== SKILLS ===")
    for skill in parsed_data.get("skills", []):
        output_lines.append(f"- {skill}")

    # Certifications
    if parsed_data.get("certifications"):
        output_lines.append("\n=== CERTIFICATIONS ===")
        for cert in parsed_data["certifications"]:
            output_lines.append(f"- {cert}")

    # Awards
    if parsed_data.get("awards"):
        output_lines.append("\n=== AWARDS ===")
        for award in parsed_data["awards"]:
            output_lines.append(f"- {award}")

    return "\n".join(output_lines)


def format_json(parsed_data: Dict[str, Any], pretty: bool = True) -> str:
    """Converts parsed data to JSON format."""
    if pretty:
        return json.dumps(parsed_data, indent=4, ensure_ascii=False)
    return json.dumps(parsed_data, ensure_ascii=False)


def save_to_text_file(parsed_data: Dict[str, Any], file_path: str) -> None:
    """Saves formatted console output to a text file."""
    content = format_console(parsed_data)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def save_to_json_file(parsed_data: Dict[str, Any], file_path: str, pretty: bool = True) -> None:
    """Saves parsed data as JSON file."""
    content = format_json(parsed_data, pretty=pretty)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def save_json_for_web(parsed_data: Dict[str, Any], file_path: str) -> None:
    """
    Saves parsed data as a JSON file optimized for frontend use.
    Ensures proper UTF-8 encoding and no extra Python data types.
    """
    output_dir = os.path.dirname(file_path)
    if output_dir: # Only create directory if path is not empty (i.e., not saving to current directory)
        os.makedirs(output_dir, exist_ok=True)

    clean_data = {
        "personal_info": parsed_data.get("personal_info", {}),
        "education": list(parsed_data.get("education", [])),
        "experience": parsed_data.get("experience", []),
        "skills": parsed_data.get("skills", []),
        "certifications": parsed_data.get("certifications", []),
        "awards": parsed_data.get("awards", [])
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)

    print(f"💾 JSON saved for web: {file_path}")

def save_to_pdf(parsed_data: Dict[str, Any], file_path: str) -> None:
    """Saves parsed data as a neatly formatted PDF file."""

    if not FPDF:
        raise ImportError("fpdf library not installed. Run `pip install fpdf` to enable PDF export.")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, sanitize_text("Resume Extract"), ln=True)

    pdf.set_font("Arial", "", 12)

    def add_section(title: str, items: list[str]):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, sanitize_text(title), ln=True)
        pdf.set_font("Arial", "", 12)
        for item in items:
            pdf.multi_cell(0, 8, sanitize_text(f"- {item}"))

    # Personal Information
    personal_info_lines = [
        sanitize_text(f"{k.capitalize()}: {v}")
        for k, v in parsed_data.get("personal_info", {}).items()
    ]
    add_section("Personal Information", personal_info_lines)

    # Education
    education_lines = [sanitize_text(str(edu)) for edu in parsed_data.get("education", [])]
    add_section("Education", education_lines)

    # Experience
    experience_lines = []
    for exp in parsed_data.get("experience", []):
        if isinstance(exp, dict):
            exp_str = ", ".join(f"{k.capitalize()}: {v}" for k, v in exp.items())
            experience_lines.append(sanitize_text(exp_str))
        else:
            experience_lines.append(sanitize_text(str(exp)))
    add_section("Experience", experience_lines)

    # Skills
    skills_lines = [sanitize_text(str(skill)) for skill in parsed_data.get("skills", [])]
    add_section("Skills", skills_lines)

    # Certifications
    if parsed_data.get("certifications"):
        cert_lines = [sanitize_text(str(cert)) for cert in parsed_data["certifications"]]
        add_section("Certifications", cert_lines)

    # Awards
    if parsed_data.get("awards"):
        award_lines = [sanitize_text(str(award)) for award in parsed_data["awards"]]
        add_section("Awards", award_lines)

    pdf.output(file_path)