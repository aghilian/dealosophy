import pandas as pd
import time
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

# Create the assistant
assistant = client.beta.assistants.create(
    name="Data Extractor",
    instructions="You answer questions about a company based on your knowledge of the company files.",
    tools = [{'type':'file_search'}],
    model = 'gpt-4o'
)

assistant.id

# Create a vector store caled "Company Policies"
vector_store = client.beta.vector_stores.create(name="Company Data")
 
# Ready the files for upload to OpenAI
file_paths = ["wood5.pdf"]
file_streams = [open(path, "rb") for path in file_paths]
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# Update the assistant with the vector store id(s)
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
    # assistant_id='asst_NLEskiKYda13bLcJtKNeZ1FV',
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Create a thread
thread = client.beta.threads.create()

thread.id

# Create our first message. The answer to this question can be found in the PDF document which was uploaded later.
message_1 = client.beta.threads.messages.create(
    thread_id = thread.id,
    role = 'user',
    content = """
        Extract the income statement as JSON, where the first object is "Years" as key 
        and values being an array of years for which data is reported. 
        The number of years available sets the fixed length of all the following arrays.
        The second and all the proceeding keys will be the account or items reported in the 
        income statement, each paired with the value as an array of fixed length that includes 
        the numbers reported for that account for the corresponding year.
        Wherever no number is reported insert a zero. 
        If you come across a category heading include it as a key with the value being an array 
        of the same lengths as all the other arrays that includes the blank string repeated.
        For all the accounts that are subcategories to a category heading, insert 3 spaces
        before the account name in the key. For sub-subcategories insert 3 more spaces and so on.
        If you find columns that only include percentage values ignore those.
        If you come across a row with first cell empty but it includes numbers, 
        then it must be a sum and use your knowledge of finance and give the key 
        a meaningful finance title like "COGS" or "Normalized EBITDA".
        If there are any visible gaps between the table rows, insert "Gap1" 
        (and "Gap2", etc if there are more) as key and empty strings inside the array.
        Meticulously continue until you have accurately captured every single piece of data 
        in the income statement. No row should be missing from your result.
        Do not put any explaination, only output the raw json output. 
        Do not prefix with any text such as json or put any quotations around the values. 
        Format the JSON like this example:
        {
            "Years" : [2022, 2023, 2024],
            "Revenue" : [number, number, number],
            "Cost of Sales" : ["", "", ""],
            "Materials" : [number, number, number],
            "Wages and employee benefits" : [number, number, number],
            "Subcontactors" : [number, number, number],
            "" : [number, number, number],
            "Gap1" : ["", "", ""],
            "Gross Profit" : [number, number, number]
        }
"""
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
    time.sleep(2)  # Wait 2 seconds before checking again
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

# Now fetch messages
messages = client.beta.threads.messages.list(
    thread_id = thread.id,
    order = 'asc'
)

# Extract only the last assistant response
assistant_response = None

for message in messages:
    if message.role == "assistant" and hasattr(message, "content") and message.content:
        assistant_response = message.content[0].text.value  # Save the latest response

# Print the clean JSON response (only once)
if assistant_response:
    try:
         # Remove triple backticks and "json" keyword (if present)
        cleaned_response = assistant_response.strip("```json").strip("```").strip()
        # Format and pretty-print JSON
        parsed_json = json.loads(cleaned_response)  # Parse the string into a JSON object
        print(json.dumps(parsed_json, indent=4))  # Pretty-print the JSON
    except json.JSONDecodeError:
        print("Received response is not valid JSON:", assistant_response)
else:
    print("No valid response received.")
    
# write to a file
with open("income_statement.json", "w") as f:
    json.dump(parsed_json, f, indent=4)

# Convert JSON to a structured DataFrame
df = pd.DataFrame.from_dict(parsed_json, orient="index")

# Rename the index column
df.index.name = "Year"


# Transpose so that accounts are rows and years are columns
df = df.transpose()

# Rename the index column to "Year"
df.index.name = "Year"

# Save to Excel file
excel_filename = "income_statement.xlsx"
df.to_excel(excel_filename, sheet_name="Income Statement", index=True)

print(f"Excel file saved: {excel_filename}")


# Add a new file to the vector store, this time in a PDF format. Note, you don't need to update the assistant again
# as it's referring to the vector store id which has not changed.
# file_02_path = "policies/health-and-safety-policy.pdf"
# file_02_stream = open(file_02_path, "rb")

# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#   vector_store_id=vector_store.id, files=[file_02_stream]
# )
    

# Delete the assistant:
response = client.beta.assistants.delete(assistant.id)

response

