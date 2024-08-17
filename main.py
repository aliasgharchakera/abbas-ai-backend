import os
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Configure the Gemini model
genai.configure()

def run_gemini(prompt):
    model = genai.GenerativeModel("gemini-pro")  # Replace with your desired Gemini model
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        doc = fitz.open(pdf_file_path)
        text = "".join(page.get_text() for page in doc)
        return text

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    pdf_file_path = data.get("pdf_file_path")
    
    if not pdf_file_path or not os.path.exists(pdf_file_path):
        return jsonify({"error": "Invalid PDF file path"}), 400
    
    text = extract_text_from_pdf(pdf_file_path)
    prompt = f"Use the following information to respond: {text}"
    
    user_message = data.get("message")
    if user_message:
        prompt += f"\n\nUser: {user_message}"
    
    response = run_gemini(prompt)
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run()
