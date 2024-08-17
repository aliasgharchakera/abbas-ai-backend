import google.generativeai as genai
from dotenv import load_dotenv
import fitz

load_dotenv()

def run_gemini(prompt):
    genai.configure()
    model = genai.GenerativeModel("gemini-pro")  # Replace with desired model
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        doc = fitz.open(pdf_file_path)
        text = "".join(page.get_text() for page in doc)
        return text

def send_pdf_to_gemini(pdf_file_path):
    text = extract_text_from_pdf(pdf_file_path)
    prompt = f"Summarize the following text: {text}"
    return run_gemini(prompt)

if __name__ == "__main__":
    pdf_file_path = "Case-study-of-ERP-implementation.pdf"  # Replace with your PDF file path
    response = send_pdf_to_gemini(pdf_file_path)
    print(response)