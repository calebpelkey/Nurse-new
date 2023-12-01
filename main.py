import streamlit as st
import os
from time import sleep
from packaging import version
from PyPDF2 import PdfReader
import docx
import functions
import io
import requests
import json
import openai


def handle_query(query, document_text, api_key, model):
    # Add a reference to the nursing knowledge base in the prompt
    prompt = f"Based on the nursing resume knowledge base:\n\n{document_text}\n\nUser: {query}\nAI:"
    response = get_openai_chat_response(api_key, model, prompt, max_tokens=250)
    return response

# Function to extract text from PDF
def extract_text_from_pdf(file_stream):
    reader = PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_stream):
    doc = docx.Document(file_stream)
    text = [paragraph.text for paragraph in doc.paragraphs]
    return '\n'.join(text)

def get_openai_chat_response(api_key, model, prompt, max_tokens):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    return response.json()

def main():
    st.title("Nursing Resume Assistant")

    # Load the OpenAI API key from Streamlit secrets
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    model = "gpt-4-1106-preview"  # Define the model here

    # Document upload and text extraction
    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt"])
    document_text = ""
    if uploaded_file is not None:
        # Process the file based on its type
        if uploaded_file.type == "application/pdf":
            document_text = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            document_text = extract_text_from_docx(io.BytesIO(uploaded_file.read()))
        else:
            document_text = uploaded_file.getvalue().decode("utf-8")

    # User input for questions
    user_input = st.text_input("Enter your query related to the uploaded document:")
    if st.button("Get AI Response"):
        try:
            response = handle_query(user_input, document_text, openai_api_key, model)

            # Display the response
            if response.get('choices'):
                last_message = response['choices'][0]['message']['content']
                st.write("Response from OpenAI:", last_message)
            else:
                st.error("No response received from OpenAI.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
