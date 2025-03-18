import time
import json
import re
import sys
import os
from prompts import *
from openai import OpenAI
from dotenv import load_dotenv
from config import BASE_DIR
from financial_analysis import analyze_json_file
load_dotenv()

def setup_openai_resources(file_paths):
    client = OpenAI()
    
    # Create the assistant
    assistant = client.beta.assistants.create(
        name="Data Extractor",
        instructions="You are great at extracting data from files and and a master CFO.",
        tools = [{'type':'file_search'}],
        model = 'gpt-4-turbo'
    )

    # Create a vector store 
    vector_store = client.beta.vector_stores.create(name="Company Data")
    
    # Open all valid files for uploading
    file_streams = [open(path, "rb") for path in file_paths]

    # Upload files and poll status
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    print(f"✅ Uploaded {len(file_streams)} files to OpenAI")

    # Update the assistant with the vector store id(s)
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    # Create a thread
    thread = client.beta.threads.create()
    
    # Return the resources needed for other functions
    return client, assistant.id, thread.id, vector_store.id

# def check_data_existence(prompt, filenames, data_type):
#     """
#     Optimized version: Queries OpenAI **once** for all files instead of looping.
#     Saves a JSON file containing filenames and page numbers where data is found.
#     """
#     # Query OpenAI Assistant for all files in one go
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role='user',
#         content=prompt
#     )

#     run = client.beta.threads.runs.create(
#         assistant_id=assistant.id,
#         thread_id=thread.id
#     )

#     while run.status not in ["completed", "failed", "cancelled"]:
#         print(f"Waiting for completion... Current status: {run.status}")
#         time.sleep(5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

#     # Fetch the latest assistant response
#     messages = client.beta.threads.messages.list(thread_id=thread.id, order='desc', limit=1)

#     assistant_response = None
#     for message in messages:
#         if message.role == "assistant" and hasattr(message, "content") and message.content:
#             assistant_response = message.content[0].text.value
#             break  # Only process the first valid response

#     print("Raw Assistant Response:", assistant_response)

#     data_locations = {}  # Default empty dict

#     if assistant_response:
#         try:
#             # Clean JSON response
#             cleaned_response = assistant_response.strip().strip("```json").strip("```").strip()
#             data_locations = json.loads(cleaned_response)  # Directly use parsed response!

#         except json.JSONDecodeError:
#             print("Invalid JSON response received. Skipping processing...")

#     # Debugging: Check data before saving
#     print("Data locations before saving:", data_locations)

#     # Save JSON file if data was found, otherwise return "Not Found"
#     output_file = os.path.join(location_folder, f"location_{data_type.lower().replace(' ', '_')}.json")

#     if data_locations:
#         with open(output_file, "w") as f:
#             json.dump(data_locations, f, indent=4)
#         print(f"{data_type} locations saved to {output_file}")
#         return data_locations
#     else:
#         print(f"No relevant {data_type} data found. Saving 'Not Found' response.")
#         not_found_result = {"Not Found": data_type}
#         with open(output_file, "w") as f:
#             json.dump(not_found_result, f, indent=4)
#         return not_found_result

def extract_and_save(client, assistant_id, thread_id, prompt, filename):
    """Function to extract financial data and save as JSON"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # ✅ Ensure json_files/ is created before saving
    
    # Create the message
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=prompt
    )
    
    # Create a run for the thread
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread_id
    )

    # Wait for the assistant to complete the run
    while run.status not in ["completed", "failed", "cancelled"]:
        print(f"Waiting for completion... Current status: {run.status}")
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Now fetch messages
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        order='asc'
    )

    # Extract only the last assistant response
    assistant_response = None
    for message in messages:
        if message.role == "assistant" and hasattr(message, "content") and message.content:
            assistant_response = message.content[0].text.value
            #print(assistant_response)
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
            #parsed_json = {key.strip(): value for key, value in parsed_json.items()}  # Trim spaces in keys
            
            #print(json.dumps(parsed_json, indent=4))  # Pretty-print JSON
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

def extractor(sender_email, folder_count, message_id_reply):
        
    user_email = sender_email
    user_history_count = str(folder_count)
    message_id = message_id_reply
    
    print("✝️ extract_data received from email_fetcher.py", user_email, user_history_count, message_id)

    # Define paths using os.path.join for cross-platform compatibility
    USER_FOLDER_PATH = os.path.join(BASE_DIR, "users", user_email)

    # ✅ Define relative paths using os.path.join and USER_FOLDER_PATH
    attachments_folder = os.path.join(USER_FOLDER_PATH, user_history_count, "attachments")
    file_paths = attachments_folder
    print(attachments_folder)
    
    json_folder = os.path.join(USER_FOLDER_PATH, user_history_count, "json_files")
    #location_folder = os.path.join(USER_FOLDER_PATH, user_history_count, "locations")

    # ✅ Ensure required directories exist
    os.makedirs(json_folder, exist_ok=True)
    #os.makedirs(location_folder, exist_ok=True)

    # ✅ Verify attachments folder exists
    if not os.path.exists(attachments_folder):
        print(f"❌ ERROR: Attachments folder does not exist: {attachments_folder}")
        sys.exit(1)

    # ✅ Define acceptable file formats for OpenAI processing
    ACCEPTABLE_FORMATS = (".pdf", ".docx", ".xlsx", ".csv", ".txt")  

    # ✅ Find all valid attachment files
    file_paths = [os.path.join(attachments_folder, file) 
                for file in os.listdir(attachments_folder) 
                if file.lower().endswith(ACCEPTABLE_FORMATS)]

    if not file_paths:
        print(f"❌ No valid files found in {attachments_folder}")
        sys.exit(1)

    print(f"\n📂 Files found for processing: {file_paths}")  # Debugging log

    if not file_paths:
        print(f"❌ No valid files found in {attachments_folder}")
        sys.exit(1)

    
     # Set up OpenAI resources
    client, assistant_id, thread_id, vector_store_id = setup_openai_resources(file_paths)
    
    # Locate Income Statement(s)
    #check_data_existence(INCOME_STATEMENT_LOCATE, file_paths, "income statement")

    # # Extract Company Info
    extract_and_save(client, assistant_id, thread_id, COMPANY_INFO_PROMPT, os.path.join(json_folder, "company_info.json"))

    # # Extract Income Statement
    extract_and_save(client, assistant_id, thread_id, INCOME_STATEMENT_PROMPT, os.path.join(json_folder, "income_statement.json"))

    # # Extract Balance Sheet
    extract_and_save(client, assistant_id, thread_id, BALANCE_SHEET_PROMPT, os.path.join(json_folder, "balance_sheet.json"))

    # # Extract Adjustments
    extract_and_save(client, assistant_id, thread_id, ADJUSTMENTS_PROMPT, os.path.join(json_folder, "adjustmentst.json"))

    # # Extract Summary
    extract_and_save(client, assistant_id, thread_id, SUMMARY_PROMPT, os.path.join(json_folder, "summary.json"))
    
    # Send json.summary file to financial_analysis.py
    summary_path = os.path.join(json_folder, "summary.json")
    if os.path.exists(summary_path):
        print(f"✅ Found summary.json file at: {summary_path}")
        # Analyze the file
        return analyze_json_file(summary_path)
    else:
        print(f"❌ summary.json not found in: {json_folder}")
        return None


    # # Extract Cash Flow Statement
    # #extract_and_save(CASH_FLOW_STATEMENT_PROMPT, "cash_flow_statement.json")

    # Delete the assistant:
    response = client.beta.assistants.delete(assistant_id)
    print("Assistant deleted.")

