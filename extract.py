import pandas as pd
import time
import json
import re
from prompts import INCOME_STATEMENT_PROMPT, BALANCE_SHEET_PROMPT, CASH_FLOW_STATEMENT_PROMPT
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

# Create the assistant
assistant = client.beta.assistants.create(
    name="Data Extractor",
    instructions="You answer questions about a company based on your knowledge of the company files.",
    tools = [{'type':'file_search'}],
    model = 'gpt-4-turbo'
)

# Create a vector store 
vector_store = client.beta.vector_stores.create(name="Company Data")
 
# Ready the files for upload to OpenAI
file_paths = [r"pdfs\sp.pdf"]
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

# Debugging: Print assistant details
# print("Updated assistant:", assistant)

# Create a thread
thread = client.beta.threads.create()

# Debugging: Print thread details
# print("Created thread:", thread)

# Create our first message. The answer to this question can be found in the PDF document which was uploaded later.
message_1 = client.beta.threads.messages.create(
    thread_id = thread.id,
    role = 'user',
    content = INCOME_STATEMENT_PROMPT
)

# Create a run for the thread
run = client.beta.threads.runs.create(
    assistant_id = assistant.id,
    thread_id = thread.id)

run.status

# Retrieve a run
run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id)

run.status

# Wait for the assistant to complete the run
while run.status not in ["completed", "failed", "cancelled"]:
    print(f"Waiting for completion... Current status: {run.status}")
    time.sleep(5)  # Wait 2 seconds before checking again
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

# Debugging: Print final run status
print("Final run status:", run)

# Now fetch messages
messages = client.beta.threads.messages.list(
    thread_id = thread.id,
    order = 'asc'
)

# Debugging: Print all messages
print("Messages from assistant:", messages)

# Extract only the last assistant response
assistant_response = None

for message in messages:
    if message.role == "assistant" and hasattr(message, "content") and message.content:
        assistant_response = message.content[0].text.value  # Save the latest response
        print(assistant_response)

# Debug: Print raw response before processing
print("Raw assistant response:", assistant_response)

# Ensure we only process valid responses
parsed_json = None

# Print the clean JSON response (only once)
if assistant_response:
    try:
         # Remove triple backticks and "json" keyword (if present)
        cleaned_response = assistant_response.strip("```json").strip("```").strip()
        
        # Remove any extraneous text at the end using regex (fix for   issue)
        cleaned_response = re.sub(r"【.*?】$", "", cleaned_response).strip()
        # Format and pretty-print JSON
        parsed_json = json.loads(cleaned_response)  # Parse the string into a JSON object
        print(json.dumps(parsed_json, indent=4))  # Pretty-print the JSON
    except json.JSONDecodeError:
        print("Received response is not valid JSON:", assistant_response)
else:
    print("No valid response received.")
    
# write to a file
if parsed_json:
    with open("income_statement.json", "w") as f:
        json.dump(parsed_json, f, indent=4)
    print("Income statement saved successfully.")
else:
    print("No valid JSON received. Skipping file write.")

# Delete the assistant:
response = client.beta.assistants.delete(assistant.id)
print("Assistant deleted.")
