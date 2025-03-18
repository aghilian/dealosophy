import json_to_excel 

# Create an Excel file from the JSON files
json_path = r"C:\dealosophy\users\iman@opensails.ca\3"
excel_file = json_to_excel.create_excel_file(json_path)
print(f"📊 Excel file created: {excel_file}")