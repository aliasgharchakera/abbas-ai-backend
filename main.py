import os
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_session import Session
import csv

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
csv_content = None
chat = None

def run_gemini(message):
    global chat
    model = genai.GenerativeModel("gemini-pro")  # Replace with your desired Gemini model
    if not chat:
        session["context"] = [
            {"role": "user", "parts": f"""
				Your general instructions: <>
                You are an intelligent assistant designed to help users understand the domain knowledge of our project and guide them to the relevant team members. You have access to detailed information about the team, including their roles, departments, and areas of ownership. You also have access to a document with comprehensive project details.
				Here is the project document:
				{pdf_content}

				Here is the csv containing the information regarding the project members and their roles
				{csv_content}

				When users ask questions or need assistance, your role is to:

				Provide Relevant Domain Information: Offer concise and accurate explanations or information based on the project details.

				Guide to Relevant Team Members: Identify the appropriate team member(s) based on the query and direct the user to them, considering their department, role, and ownership area.

				If a user inquires about a specific area (e.g., "Who handles Infrastructure?" or "Who can I talk to about Utilities?"), you should refer them to the correct person or provide a brief explanation from the project document if needed.

				Always be clear, concise, and user-friendly in your responses.
				
				If you are unsure about the answer, you can ask the user to clarify their question or provide additional context.
    
				<>
             """},
            {"role": "model", "parts": f"""
                Ok, I understand. Let's get started!
             """}
        ]
        chat = model.start_chat(history=session["context"])
    response = chat.send_message(message)
    return response.text

def extract_text_from_pdf(pdf_file_path):
	doc = fitz.open(pdf_file_path)
	text = "".join(page.get_text() for page in doc)
	return text

def extract_text_from_csv(csv_file_path):
	with open(csv_file_path, 'r') as file:
		reader = csv.reader(file)
		text = "".join(row[0] for row in reader)
	return text

with app.app_context():
    # Load the PDF content once when the app starts
    pdf_file_path = "Case-study-of-ERP-implementation.pdf"
    csv_file_path = "team_members - Sheet1.csv"
    pdf_content = extract_text_from_pdf(pdf_file_path)
    csv_content = extract_text_from_csv(csv_file_path)
    
@app.route('/', methods=['GET'])
def index():
    return {"message": "Welcome to the Abbas AI Chatbot!"}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    global pdf_content
    user_message = data.get("message")
    
    if not pdf_content or not user_message:
        return jsonify({"error": "PDF content and user message are required"}), 400

    # # Initialize session context if it doesn't exist
    # if "context" not in session:
    #     session["context"] = [
    #         {"role": "system", "content": f"Use the following information to respond: {pdf_content}"}
    #     ]
    
    # # Append the user message to the context
    # session["context"].append({"role": "user", "content": user_message})
    
    # Generate a response with Gemini using the conversation context
    response_text = run_gemini(user_message)
    
    # # Append the model's response to the context
    # session["context"].append({"role": "model", "content": response_text})
    
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=os.environ.get("DEBUG", False))
