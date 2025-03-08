# prompts.py

INCOME_STATEMENT_LOCATE = """
You are analyzing multiple financial documents. Your task is to identify the exact location of the Income Statement (also known as the Profit and Loss Statement) in each document.

Strict Guidelines:
Do not extract the actual Income Statement data.
Focus only on the Income Statement. Ignore other financial tables such as the Balance Sheet, Cash Flow Statement, EBITDA Adjustments, Seller’s Discretionary Earnings, etc.
Scan all uploaded files and return results only for files where the Income Statement is found.
If found, return a valid JSON object where:
The filename is the key.
The value is an array of sequential page numbers (not printed page numbers) where the Income Statement appears.
- If no Income Statement is found in any file, return: { "Not Found": "Income Statement" }

Example Response (if Income Statements are found in 2 out of 6 files):
{
    "file1.pdf": [3, 4, 5],
    "file3.pdf": [7, 8]
}
Only return a valid json file with no extra characters or comments.
"""


INCOME_STATEMENT_PROMPT = """
You are an experienced CFO.
Analyze the file and identify the income statement or profit and loss statement, which may span multiple pages and be presented in one or more tables. Ensure all tables contributing to the income statement are considered.  

### Extraction Guidelines:  
- Extract the income statement as **valid JSON**.  
- The first key must be `"Years"`, with its value being an array of all reported years. This determines the fixed length of all other arrays.  
- Each subsequent key represents an account or item from the income statement, with values being arrays of the same fixed length, containing reported numbers.  
- If a value is missing, insert an **empty string** (`""`).  

### Formatting Rules:  
1. **Category Headings:** Include as keys with values as arrays of empty strings matching the fixed length.  
2. **Indented Subcategories:**  
   - Prefix subcategories with **three spaces**.  
   - Sub-subcategories get **three additional spaces**, and so on.  
3. **Percentage Columns:** Ignore columns that contain only percentage values.  
4. **Unnamed Rows with Numbers:** If a row has no label but contains numbers, infer a **meaningful finance-related title** (e.g., `"COGS"` or `"Normalized EBITDA"`).  
5. **Correcting Errors:** If a key contains **typos or formatting issues**, correct them (e.g., `"Uti l i ties"` → `"Utilities"`, `"Professjonal fees"` → `"Professional fees"`).  
6. **Visible Row Gaps:** If the table has visible gaps, insert `"Gap1"`, `"Gap2"`, etc., as keys, each with an array of empty strings.  
7. **Consistency Check:** Ensure all arrays have the **same length** as `"Years"`. If shorter, pad with empty strings.  

### Output Format Example:  
```json
{
    "Years": [2022, 2023, 2024],
    "Revenue": [number, number, number],
    "Cost of Sales": ["", "", ""],
    "   Materials": [number, number, number],
    "   Wages and employee benefits": [number, number, number],
    "   Subcontractors": [number, number, number],
    "   ": [number, number, number], 
    "Gap1": ["", "", ""],
    "Gross Profit": [number, number, number]
}
```  

### If No Income Statement is Found:  
If no income statement or relevant table is identified, return:  
```json
{
    "Not Found": "Income Statement"
}
```  

### Final Checks:  
- Ensure the JSON is **valid and correctly formatted**.  
- **Do not** include any explanations, extra text, or unnecessary quotations.  
- **Thoroughly verify** that no row is missing and all data is structured properly.
"""

BALANCE_SHEET_LOCATE = """
You are analyzing multiple financial documents. Your task is to locate the **Balance Sheet** section in each document and provide only its location details.

- **Do not extract the actual Balance Sheet data.**
- **Check all uploaded files** and return results only for files where the Balance Sheet is found.
- If found, return a JSON object where:
  - The filename is the key.
  - The value is an array of page numbers where the Balance Sheet appears.
- If no Balance Sheet is found in any file, return: `{ "Not Found": "Balance Sheet" }`

### **Example Response (if Balance Sheets are found in 2 out of 3 files):**  
```json
{
    "file1.pdf": [3, 4, 5],
    "file3.pdf": [7, 8]
}

### **Example Response (if not found):**  
```json
{
    "Not Found": "Balance Sheet"
}
```

Carefully scan the document, ensuring accuracy in locating the Balance Sheet section.
```
Only return a valid json file with no extra characters or comments.
"""

BALANCE_SHEET_PROMPT = """
You are an experienced CFO.
Analyze the file and identify the **balance sheet**, ensuring that it is not mistaken for an income statement. The balance sheet may span multiple pages and be reported in one or more tables. Consider all relevant tables to construct a complete balance sheet.  

### **Extraction Guidelines:**  
- Extract the balance sheet as **valid JSON**.  
- The first key must be `"Years"`, with its value being an array of all reported years. This determines the fixed length of all other arrays.  
- Each subsequent key represents an account or item from the balance sheet, with values being arrays of the same fixed length, containing reported numbers.  
- If a value is missing, insert an **empty string** (`""`).  

### **Formatting Rules:**  
1. **Category Headings:** Include as keys with values as arrays of empty strings matching the fixed length.  
2. **Indented Subcategories:**  
   - Prefix subcategories with **three spaces**.  
   - Sub-subcategories get **three additional spaces**, and so on.  
3. **Percentage Columns:** Ignore columns that contain only percentage values.  
4. **Unnamed Rows with Numbers:** If a row has no label but contains numbers, infer a **meaningful finance-related title** (e.g., `"Total Current Assets"` or `"Total Liabilities"`).  
5. **Correcting Errors:** If a key contains **typos or formatting issues**, correct them (e.g., `"Uti l i ties"` → `"Utilities"`, `"Professjonal fees"` → `"Professional fees"`).  
6. **Visible Row Gaps:** If the table has visible gaps, insert `"Gap1"`, `"Gap2"`, etc., as keys, each with an array of empty strings.  
7. **Consistency Check:** Ensure all arrays have the **same length** as `"Years"`. If shorter, pad with empty strings.  

### **Output Format Example:**  
```json
{
    "Years": [2022, 2023, 2024],
    "Current Assets": ["", "", ""],
    "   Cash": [number, number, number],
    "   Accounts Receivable": [number, number, number],
    "Gap1": ["", "", ""],
    "Total Current Assets": [number, number, number]
}
```  

### **If No Balance Sheet is Found:**  
If no balance sheet or relevant table is identified, return:  
```json
{
    "Not Found": "Balance Sheet"
}
```  

### **Final Checks:**  
- Ensure the JSON is **valid and correctly formatted**.  
- **Do not** include any explanations, extra text, or unnecessary quotations.  
- **Thoroughly verify** that no row is missing and all data is structured properly.
"""

CASH_FLOW_STATEMENT_PROMPT = """
You are an experienced CFO.
Analyze the file and identify the **cash flow statement**, ensuring it is not mistaken for an income statement. The cash flow statement reports the movement of cash, typically starting with the **beginning cash balance**, listing all **cash inflows and outflows**, and ending with the **cash balance at the end of the year**. The statement may span multiple pages and be reported in one or more tables. Consider all relevant tables to construct a complete cash flow statement.  

### **Extraction Guidelines:**  
- Extract the cash flow statement as **valid JSON**.  
- The first key must be `"Years"`, with its value being an array of all reported years. This determines the fixed length of all other arrays.  
- Each subsequent key represents an account or item from the cash flow statement, with values being arrays of the same fixed length, containing reported numbers.  
- If a value is missing, insert an **empty string** (`""`).  

### **Formatting Rules:**  
1. **Category Headings:** Include as keys with values as arrays of empty strings matching the fixed length.  
2. **Indented Subcategories:**  
   - Prefix subcategories with **three spaces**.  
   - Sub-subcategories get **three additional spaces**, and so on.  
3. **Percentage Columns:** Ignore columns that contain only percentage values.  
4. **Unnamed Rows with Numbers:** If a row has no label but contains numbers, infer a **meaningful finance-related title** (e.g., `"Net Cash Provided by Operating Activities"` or `"Total Cash Flow"`).  
5. **Correcting Errors:** If a key contains **typos or formatting issues**, correct them (e.g., `"Uti l i ties"` → `"Utilities"`, `"Professjonal fees"` → `"Professional fees"`).  
6. **Visible Row Gaps:** If the table has visible gaps, insert `"Gap1"`, `"Gap2"`, etc., as keys, each with an array of empty strings.  
7. **Consistency Check:** Ensure all arrays have the **same length** as `"Years"`. If shorter, pad with empty strings.  

### **Output Format Example:**  
```json
{
    "Years": [2022, 2023, 2024],
    "Cash and Cash Equivalents, Beginning of Year": [number, number, number],
    "Activity": ["", "", ""],
    "   Cash Generated by Operating Activities": [number, number, number],
    "   Cash Used in Investing Activities": [number, number, number],
    "Increase / Decrease in Cash and Cash Equivalents": [number, number, number],
    "Cash and Cash Equivalents, End of Year": [number, number, number]
}
```  

### **If No Cash Flow Statement is Found:**  
If no cash flow statement or relevant table is identified, return:  
```json
{
    "Not Found": "Cash Flow Statement"
}
```  

### **Final Checks:**  
- Ensure the JSON is **valid and correctly formatted**.  
- **Do not** include any explanations, extra text, or unnecessary quotations.  
- **Thoroughly verify** that no row is missing and all data is structured properly.
"""

ADJUSTMENTS_PROMPT = """
You are an experienced CFO.
Analyze the file and search for the words Addbacks or Seller's Discretionary Earnings (SDE) and thus find a **financial table** that may be titled **EBITDA Normalization, EBITDA Adjustments, Addbacks, or Seller’s Discretionary Earnings (SDE)** or something similar. This table may span multiple pages and be reported in one or more tables. Consider all relevant tables to construct a complete dataset.  
Make sure you are not mixing it up with income statement or balance sheet.
### **Extraction Guidelines:**  
- Extract the adjustments as **valid JSON**.  
- The first key must be `"Years"`, with its value being an array of all reported years. This determines the fixed length of all other arrays.  
- Each subsequent key represents an adjustment or addback item from the table, with values being arrays of the same fixed length, containing reported numbers.  
- If a value is missing, insert an **empty string** (`""`).  

### **Formatting Rules:**  
1. **Category Headings:** Include as keys with values as arrays of empty strings matching the fixed length.  
2. **Indented Subcategories:**  
   - Prefix subcategories with **three spaces**.  
   - Sub-subcategories get **three additional spaces**, and so on.  
3. **Percentage Columns:** Ignore columns that contain only percentage values.  
4. **Unnamed Rows with Numbers:** If a row has no label but contains numbers, infer a **meaningful finance-related title** (e.g., `"Total Addbacks"` or `"Total Adjustments"`).  
5. **Correcting Errors:** If a key contains **typos or formatting issues**, correct them (e.g., `"Mea ls"` → `"Meals"`, `"Professjonal fees"` → `"Professional fees"`).  
6. **Visible Row Gaps:** If the table has visible gaps, insert `"Gap1"`, `"Gap2"`, etc., as keys, each with an array of empty strings.  
7. **Consistency Check:** Ensure all arrays have the **same length** as `"Years"`. If shorter, pad with empty strings.  

### **Output Format Example:**  
```json
{
    "Years": [2022, 2023, 2024],
    "Amortization": [number, number, number],
    "Management Salaries": ["", "", ""],
    "   Vehicles": [number, number, number],
    "   Life Insurance": [number, number, number],
    "   Meals and Entertainment": [number, number, number],
    "Total Addbacks": [number, number, number]
}
```  

### **If No Relevant Table is Found:**  
If no EBITDA adjustments, addbacks, or SDE table is identified, return:  
```json
{
    "Not Found": "EBITDA Adjustments"
}
```  

### **Final Checks:**  
- Ensure the JSON is **valid and correctly formatted**.  
- **Do not** include any explanations, extra text, or unnecessary quotations.  
- **Thoroughly verify** that no row is missing and all data is structured properly.
"""

COMPANY_INFO_PROMPT = """
Extract the following information in this exact order about the company, and if the information is unknown, put `null`:  

- **Company's Name**  
- **Asking Price**  
- **Years in Business**  
- **Owner Name(s)**  
- **Number of Employees**  
- **Employee Info Summary**  
- **What does this business do (in less than 20 words)**  
- **Industry or industries this business operates in**  
- **Business Address**  
- **Facilities Ownership Type**  
- **Lease Per Month Rent** *(Calculate if needed: e.g., multiplying facilities area by rent per sq ft.)*  
- **Lease Renewal Status (briefly)**  
- **Location Size in Square Feet**  

### **Output Format for Company Information:**  
```json
{
    "Name": string,
    "Asking price": number,
    "Years in business": number,
    "Owner(s)": string,
    "Number of employees": number,
    "Employees": string,
    "Business info": string,
    "Industry": string,
    "Address": string,
    "Facilities ownership type": string,
    "Lease per month rent": number,
    "Lease expiry and renewal status": string,
    "Location size in Square feet": number
}
```

---

### **Extract Broker Information:**  
If any information is unknown, insert `null`:  

- **Brokerage Firm**  
- **Broker Agent Name**  
- **Broker Agent Phone Number**  
- **Broker Agent Email**  

### **Output Format for Broker Information:**  
```json
{
    "Brokerage firm": string,
    "Broker Agent": string,
    "Broker phone": string,
    "Broker email": string
}
```

### **Final Output:**  
- **Combine both dictionaries** (Company Info + Broker Info) into **one valid JSON object**.  
- **Do not include any explanations, extra text, or prefixes.**  
- **Ensure valid JSON formatting.**
"""

