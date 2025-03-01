import time
import json
import re
import sys
import os
import subprocess
from prompts import *
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

start_time = time.time()  # Start measuring time

# Get user_email and user_history_count from command-line arguments
if len(sys.argv) < 3:
    print("Error: Missing arguments. Usage: extract_data.py <user_email> <user_history_count>")
    sys.exit(1)

user_email = sys.argv[1]
user_history_count = str(sys.argv[2])  # Convert back to integer


# Get optional message_id and subject for threaded email replies
message_id = sys.argv[3] if len(sys.argv) > 3 else None
subject = sys.argv[4] if len(sys.argv) > 4 else None


print("✝️ extract_data received from email_fetcher.py", user_email, user_history_count, message_id, subject)

# ✅ Define relative paths
attachments_folder = os.path.join("users", user_email, user_history_count, "attachments")
json_folder = os.path.join("users", user_email, user_history_count, "json_files")

# ✅ Verify attachments folder exists
if not os.path.exists(attachments_folder):
    print(f"❌ ERROR: Attachments folder does not exist: {attachments_folder}")
    sys.exit(1)

# ✅ Find attachment files (Currently processing PDFs)
file_paths = [os.path.join(attachments_folder, file) for file in os.listdir(attachments_folder) if file.endswith(".pdf")]

if not file_paths:
    print(f"❌ No valid files found in {attachments_folder}")
    sys.exit(1)

client = OpenAI()

# Create the assistant
assistant = client.beta.assistants.create(
    name="Data Extractor",
    instructions="You are great at extracting data from files and you are a finance wiz and will answer questions about a company based on your knowledge of the company files.",
    tools = [{'type':'file_search'}],
    model = 'gpt-4-turbo'
)

# Create a vector store 
vector_store = client.beta.vector_stores.create(name="Company Data")
 
# Ready the files for upload to OpenAI
file_streams = [open(path, "rb") for path in file_paths]
 
# Upload and poll the status
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# Update the assistant with the vector store id(s)
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Create a thread
thread = client.beta.threads.create()

def extract_and_save(prompt, filename):
    """Function to extract financial data and save as JSON"""
    
    filename = os.path.join(json_folder, filename)  # ✅ Automatically append json_folder
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # ✅ Ensure json_files/ is created before saving
    
    # Create the message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=prompt
    )
    
    # Create a run for the thread
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id
    )

    # Wait for the assistant to complete the run
    while run.status not in ["completed", "failed", "cancelled"]:
        print(f"Waiting for completion... Current status: {run.status}")
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Now fetch messages
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order='asc'
    )

    # Extract only the last assistant response
    assistant_response = None
    for message in messages:
        if message.role == "assistant" and hasattr(message, "content") and message.content:
            assistant_response = message.content[0].text.value
            print(assistant_response)
    print("Raw Assistant Response:", assistant_response)

        # Ensure valid JSON response
    parsed_json = None
    if assistant_response:
        try:
            # Remove Markdown JSON formatting artifacts
            cleaned_response = assistant_response.strip("```json").strip("```").strip()

            # Try regex to remove unexpected text before/after JSON
            cleaned_response = re.sub(r"^[^{]*|[^}]*$", "", cleaned_response).strip()

            # Fix keys that may have unnecessary spaces
            parsed_json = json.loads(cleaned_response)
            parsed_json = {key.strip(): value for key, value in parsed_json.items()}  # Trim spaces in keys
            
            print(json.dumps(parsed_json, indent=4))  # Pretty-print JSON
        except json.JSONDecodeError:
            print("Received response is not valid JSON. Attempting cleanup...")
            print("Error Content:", assistant_response)
    else:
        print("No valid response received.")


    # Write to a file
    if parsed_json:
        with open(filename, "w") as f:
            json.dump(parsed_json, f, indent=4)
        print(f"{filename} saved successfully.")
    else:
        print("No valid JSON received. Skipping file write.")

# Extract Company Info
extract_and_save(COMPANY_INFO_PROMPT, "company_info.json")

# Extract Broker Info
# extract_and_save(BROKER_INFO_PROMPT, "broker_info.json")

# Extract Income Statement
# extract_and_save(INCOME_STATEMENT_PROMPT, "income_statement.json")

# Extract Balance Sheet
# extract_and_save(BALANCE_SHEET_PROMPT, "balance_sheet.json")

# Extract Cash Flow Statement
# extract_and_save(CASH_FLOW_STATEMENT_PROMPT, "cash_flow_statement.json")


# Delete the assistant:
response = client.beta.assistants.delete(assistant.id)
print("Assistant deleted.")

end_time = time.time()  # End measuring time
print(f"Total execution time: {end_time - start_time:.2f} seconds")

subprocess.run(["python", "json_to_excel.py", user_email, user_history_count, message_id, subject])
print("🚣‍♀️ Message info sent to json_to_excel.py", user_email, user_history_count, message_id, subject)