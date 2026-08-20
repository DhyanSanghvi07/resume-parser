# 📄 Resume Parser with LLM & Traditional NLP

This is a **Resume Parser** web application built using **Flask** (Python backend) and **JavaScript** (frontend). It allows users to upload resumes in `.pdf` or `.docx` format and parses them using a combination of **NLP techniques** and **LLM-based models**, extracting structured information and displaying it in a user-friendly format.

---

## 🚀 Features

- Upload resumes in PDF or DOCX format
- Extract:
  - Name
  - Email
  - Phone Number
  - Education
  - Work Experience
  - Skills
- Generates:
  - Structured JSON output
  - Downloadable PDF summary
- Clean UI built with static HTML/CSS/JS
- Cross-origin enabled via `flask`

---

## 🛠️ Tech Stack

### Backend:
- Python
- Flask
- spaCy
- PyMuPDF
- pdfplumber
- pdf2image
- pytesseract
- docx2txt
- fpdf

### Frontend:
- HTML/CSS
- JavaScript

---

## 📦 Installation

### Prerequisites

- Python 3.7+
- Tesseract OCR installed and added to PATH (for image parsing in PDFs)

### Clone and Install

```bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run the App

```bash
python api.py
```

#### Once the server is running, open your browser and navigate to:
http://localhost:5000

### 📁 Project Structure


### 📤 API Endpoint
`POST /parse`
- Accepts: multipart/form-data with key "resume" and file (.pdf or .docx)
- Returns: JSON with parsed resume data

### ✅ Example Output
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "education": ["B.Tech in CSE - XYZ University"],
  "experience": ["Software Engineer at ABC Corp"],
  "skills": ["Python", "Django", "Machine Learning"]
}
```

### 📄 License
This project is open-source and free to use for educational and research purposes.

### 👨‍💻 Developed by
Team Name: VESP Students

Contributors:
- Dhyan Sanghvi
- Chahat Poptani
- Vedanshi Gosalia
- Riya Gajra
- Divya Karotra
- Smit Pingale
- Ayush Gurav

### 📬 Contact
If you have any questions or suggestions, feel free to reach out at sanghviddhyan@gmail.com .
