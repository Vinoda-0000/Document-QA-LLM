import streamlit as st
import pandas as pd
from docx import Document
from pypdf import PdfReader
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit config
st.set_page_config(page_title="Document-RAG-LLM", layout="wide")
st.title("PDF Question Answering")

# Get API key securely
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found. Set it in .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

uploaded_files = st.file_uploader(
    "Upload documents (PDF, TXT, CSV, DOCX)",
    type=["pdf", "txt", "csv", "docx"],
    accept_multiple_files=True
)

def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

    elif file.type == "text/plain":
        text = file.read().decode("utf-8")

    elif file.type == "text/csv":
        df = pd.read_csv(file)
        text = df.to_string(index=False)

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

if uploaded_files:
    all_text = ""
    for file in uploaded_files:
        all_text += extract_text(file) + "\n"

    st.success("Documents loaded successfully")

    question = st.text_input("Ask a question")
    if question:
        prompt = f"""
Answer using the following document text.

{all_text[:12000]}

Question: {question}
"""
        response = model.generate_content(prompt)
        st.subheader("Answer")
        st.write(response.text)
else:
    st.info("Upload documents to start")
