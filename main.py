import os
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_session import Session

load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Configure the Gemini model
genai.configure()

# Setup Flask session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', 'supersecretkey')
Session(app)

pdf_content = None

def run_gemini(messages):
    model = genai.GenerativeModel("gemini-pro")  # Replace with your desired Gemini model
    response = model.generate_content(messages=messages)
    return response.text

def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        doc = fitz.open(pdf_file_path)
        text = "".join(page.get_text() for page in doc)
        return text

@app.before_first_request
def load_pdf():
    global pdf_content
    # Load the PDF content once when the app starts
    pdf_file_path = "Case-study-of-ERP-implementation.pdf"
    pdf_content = extract_text_from_pdf(pdf_file_path)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    global pdf_content
    user_message = data.get("message")
    
    if not pdf_content or not user_message:
        return jsonify({"error": "PDF content and user message are required"}), 400

    # Initialize session context if it doesn't exist
    if "context" not in session:
        session["context"] = [
            {"role": "system", "content": f"Use the following information to respond: {pdf_content}"}
        ]
    
    # Append the user message to the context
    session["context"].append({"role": "user", "content": user_message})
    
    # Generate a response with Gemini using the conversation context
    response_text = run_gemini(session["context"])
    
    # Append the assistant's response to the context
    session["context"].append({"role": "assistant", "content": response_text})
    
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run()
