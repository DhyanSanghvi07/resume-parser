import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from app.parser import parse_resume
from app.output_formatter import save_json_for_web

ALLOWED_EXTENSIONS = {"pdf", "docx"}
UPLOAD_FOLDER = "uploads"
OUTPUT_JSON = "output.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route("/")
def home():
    return app.send_static_file("Home Page/index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
