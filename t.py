from json_to_excel import create_excel_file

path = r"C:\dealosophy\users\iman@opensails.ca\9"
result = create_excel_file(path)
print(f"Excel file created at: {result}")