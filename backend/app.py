import os
import PyPDF2
import spacy
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API Key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

# Function to analyze contract clauses
def analyze_contract(text):
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["LAW", "ORG", "DATE", "MONEY", "GPE"]:
            entities[ent.text] = ent.label_
    return entities

# Function to summarize contract
def summarize_contract(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize this legal contract briefly."},
            {"role": "user", "content": text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

# API endpoint to upload and process a contract
@app.route("/upload", methods=["POST"])
def upload_contract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)
    
    text = extract_text_from_pdf(file_path)
    clauses = analyze_contract(text)
    summary = summarize_contract(text)
    
    return jsonify({"summary": summary, "clauses": clauses})

if __name__ == "__main__":
    app.run(debug=True)
