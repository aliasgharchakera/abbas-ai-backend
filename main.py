import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

def run_gemini(prompt):
    """Runs a Gemini query using the provided API key and prompt.

    Args:
        prompt: The query or prompt for Gemini.

    Returns:
        The Gemini model's response.
    """

    genai.configure()
    model = genai.GenerativeModel("gemini-pro")  # Replace with desired model
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(pdf_file_path):
    """Extracts text from a PDF file.

    Args:
        pdf_file_path: The path to the PDF file.

    Returns:
        The extracted text from the PDF.
    """

    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text

def send_pdf_to_gemini(pdf_file_path):
    """Sends a PDF file to Gemini for summarization by extracting text.

    Args:
        pdf_file_path: The path to the PDF file.

    Returns:
        The Gemini model's response.
    """

    text = extract_text_from_pdf(pdf_file_path)
    prompt = f"Summarize the following text: {text}"
    return run_gemini(prompt)

if __name__ == "__main__":
    pdf_file_path = "your_pdf_file.pdf"  # Replace with your PDF file path
    response = send_pdf_to_gemini(pdf_file_path)
    print(response)