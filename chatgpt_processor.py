import openai
import os
import time
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# ✅ Ensure required environment variables are set
if not OPENAI_API_KEY or not ASSISTANT_ID:
    raise ValueError("❌ Missing OpenAI API Key or Assistant ID in .env file!")

# ✅ Initialize OpenAI Client
client = openai.Client(api_key=OPENAI_API_KEY)

def upload_file_to_openai(file_path):
    """Uploads a PDF file to OpenAI and returns the file ID."""
    try:
        with open(file_path, "rb") as pdf_file:
            response = client.files.create(
                file=pdf_file,
                purpose="assistants"  # ✅ Correct purpose for OpenAI file uploads
            )
        return response.id  # ✅ Extract the file ID
    except Exception as e:
        print(f"❌ Error uploading PDF file to OpenAI: {e}")
        return None

def process_file_with_chatgpt(file_path):
    """Uploads the PDF to OpenAI, then extracts structured financial data."""
    
    file_id = upload_file_to_openai(file_path)
    if not file_id:
        return None

    try:
        # ✅ Step 1: Create a new thread
        thread = client.beta.threads.create()
        thread_id = thread.id  # ✅ Get thread ID

        # ✅ Step 2: Add a message to the thread with proper file attachment
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content="Extract all financial tables (Balance Sheet, Income Statement) from this document. Ensure proper formatting.",
            attachments=[
                {
                    "file_id": file_id,
                    "tools": [{"type": "file_search"}]  # ✅ Corrected: Properly formatted tools parameter
                }
            ]
        )

        # ✅ Step 3: Run the assistant on the thread
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # ✅ Step 4: Wait for the assistant's response
        while run.status not in ["completed", "failed"]:
            time.sleep(3)  # ✅ Check every 3 seconds
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        # ✅ Step 5: Retrieve the assistant's final response
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            extracted_data = messages.data[0].content[0].text.value
            return extracted_data

        print(f"❌ OpenAI Assistant Run Failed: {run.status}")
        return None

    except Exception as e:
        print(f"❌ Error with OpenAI API: {e}")
        return None  # Return None if an error occurs