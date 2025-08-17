import os
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from app.parser import parse_resume
from app.output_formatter import save_json_for_web, save_to_pdf

ALLOWED_EXTENSIONS = {"pdf", "docx"}
UPLOAD_FOLDER = "uploads"
OUTPUT_JSON = "output.json"
PDF_OUTPUT_DIR = "temp_pdfs" # Directory to store temporary PDFs

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

app = Flask(
    __name__,
    static_folder="Frontend",    # serve everything in Frontend/
    static_url_path=""           # so /Home Page/styles.css works
)

CORS(app)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/parse", methods=["POST"])
def parse_resume_endpoint():
    if "resume" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["resume"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
        except Exception as e:
            return jsonify({"error": f"Error saving file: {str(e)}"}), 500

        try:
            parsed_data = parse_resume(filepath)
            save_json_for_web(parsed_data, OUTPUT_JSON)
            return jsonify(parsed_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route("/output.json")
def get_output_json():
    if os.path.exists(OUTPUT_JSON):
        return send_file(OUTPUT_JSON, mimetype="application/json")
    return jsonify({"error": "No output yet"}), 404

@app.route("/download_pdf", methods=["POST"])
def download_pdf_endpoint():
    try:
        parsed_data = request.json
        if not parsed_data:
            return jsonify({"error": "No data provided for PDF generation"}), 400
        
        # Create a unique temporary file path for the PDF
        pdf_filename = secure_filename(f"resume_{os.urandom(8).hex()}.pdf")
        pdf_filepath = os.path.join(PDF_OUTPUT_DIR, pdf_filename)

        save_to_pdf(parsed_data, pdf_filepath)

        # Schedule file deletion after response is sent
        @after_this_request
        def remove_file(response):
            try:
                os.remove(pdf_filepath)
                print(f"Cleaned up temporary PDF: {pdf_filepath}")
            except Exception as e:
                print(f"Error cleaning up temporary PDF {pdf_filepath}: {e}")
            return response

        # Send the file
        return send_file(pdf_filepath, mimetype="application/pdf", as_attachment=True, download_name="parsed_resume.pdf")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@app.route("/")
def home():
    return app.send_static_file("Home Page/index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
