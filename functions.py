import json
import os
import openai

def create_assistant(client, name, description, training_data_file='/Users/calebpelkey/Desktop/Nursing_Knowledge.docx', model='gpt-4-1106-preview'):
    assistant_file_path = 'assistant.json'
    assistant_id = None

    try:
        if os.path.exists(assistant_file_path):
            with open(assistant_file_path, 'r') as file:
                assistant_data = json.load(file)
                assistant_id = assistant_data['assistant_id']
                print("Loaded existing assistant ID.")
        else:
            if os.path.exists(training_data_file):
                with open(training_data_file, "rb") as doc_file:
                    # Create the file object in the OpenAI system
                    file_object = client.files.create(file=doc_file, purpose='assistants')
            else:
                raise FileNotFoundError(f"Training data file '{training_data_file}' not found.")

            # Detailed instructions for the assistant
            instructions = (
                "Welcome to the Nursing Resume Assistant, powered by ChatGPT and specialized for international nurses. "
                "This assistant is designed to guide you through customizing your resume to meet Canadian healthcare standards, "
                "as outlined in Nursing Knowledge V2. We recommend following these steps for optimal assistance: "
                "1. Upload Your Resume: Start by uploading your current resume for analysis. "
                "2. Upload a Job Description: Next, upload a job description for a role you are interested in. "
                "3. Interactive Queries: Ask specific questions about adapting your resume to the job description and Canadian standards. "
                "4. Skill Gap Analysis: The assistant will help identify any skill gaps compared to Canadian nursing requirements. "
                "5. Resume Enhancement: Receive suggestions for improving your resume, including keyword optimization and alignment with Canadian standards. "
                "6. Tailored Advice: Get personalized advice for customizing your resume, based on your professional experience and the job you're targeting. "
                "Feel free to navigate these steps in any order, and use the provided Nursing Knowledge V2 document for detailed guidance."
            )


            # Create the assistant
            assistant = client.Assistant.create(
                name=name,
                instructions=instructions,
                model=model,
                tools=[{"type": "retrieval"}],
                file_ids=[file_object.id]  # Use the ID of the file object
            )

            # Save the assistant ID
            with open(assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)
                print("Created a new assistant and saved the ID.")

            assistant_id = assistant.id

    except Exception as e:
        print(f"Error in creating assistant: {e}")

    return assistant_id
