import streamlit as st
import os
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

    # Initialize session state for history and user input if not already present
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = ""

    # Load the OpenAI API key from an environment variable
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key is None:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    model = 'gpt-4-1106-preview'

    # Display the conversation history
    for i, (role, text) in enumerate(st.session_state['history']):
        if role == 'user':
            st.markdown(f"**User:**\n{text}", unsafe_allow_html=True)
        else:
            st.markdown(f"**AI:**\n{text}", unsafe_allow_html=True)
        if i < len(st.session_state['history']) - 1:
            st.text("")  # Add space after each entry except the last

    # Text input for user's query
    user_input = st.text_input("Enter your query related to the uploaded document:", value=st.session_state.user_input)

    # When the user sends a query
    if st.button("Get AI Response"):
        # Append user query to history
        st.session_state['history'].append(('user', user_input))

        # Call the function that communicates with OpenAI API
        response = handle_query(user_input, st.session_state.get('document_text', ""), openai_api_key, model)

        # Check if the response is valid and then update the history
        if 'choices' in response and response['choices']:
            ai_response = response['choices'][0]['message']['content']
            st.session_state['history'].append(('ai', ai_response))
        else:
            st.error("No response received from the AI.")

        # Clear the input field
        st.session_state.user_input = ""
        st.experimental_rerun()

    # The "Upload your document" section is now placed below the query input
    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        # Process the file based on its type
        if uploaded_file.type == "application/pdf":
            st.session_state['document_text'] = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            st.session_state['document_text'] = extract_text_from_docx(io.BytesIO(uploaded_file.read()))
        else:
            st.session_state['document_text'] = uploaded_file.getvalue().decode("utf-8")

if __name__ == "__main__":
    main()
