# prompts.py

INCOME_STATEMENT_PROMPT = """
        Analyze the file and carefully look for the income statement. This maybe on one
        or more than one page. It maybe reported in one table or multiple tables where you
        would have to take all into account.
        Extract the income statement as JSON, where the first object is "Years" as key 
        and values being an array of years for which data is reported. 
        The number of years available sets the fixed length of all the following arrays.
        The second and all the proceeding keys will be the account or items reported in the 
        income statement, each paired with the value as an array of fixed length that includes 
        the numbers reported for that account for the corresponding year.
        Wherever no number is reported insert an empty string. 
        If you come across a category heading include it as a key with the value being an array 
        of the same lengths as all the other arrays that includes the blank string repeated.
        For all the accounts that are subcategories to a category heading, insert 3 spaces
        before the account name in the key. For sub-subcategories insert 3 more spaces and so on.
        If you find columns that only include percentage values ignore those.
        If you come across a row with first cell empty but it includes numbers, 
        then it must be a sum and use your knowledge of finance and give the key 
        a meaningful finance title like "COGS" or "Normalized EBITDA".
        Check that all keys are meaningful words that make sense in an income statement,
        if they are not fix them to the closest word that makes sense, for example if you see "Uti l i ties"
        you can reason that it must be "Utilities" or if you see "Professjonal  fees" you can reason
        that that it must be "Professional fees" and make the correction.
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
        
        If you have thoroughly searched the document and find
        no income statement or a table that resembles an income statement
        return a json like this
        {
            "Not Found" : "Income Statement"
        }
        Return only valid JSON.
        Go back and check that each value is an array with the length equal
        to the number of years reported. If a value is an array with fewer
        objects, add few empty strings to bring the legnth of the array to
        the fixed length that we expect for all arrays.
"""

BALANCE_SHEET_PROMPT = """
        Analyze the file and carefully look for the balance sheet.
        Make sure you're not mistaking income statement for balance sheet.
        This maybe on one or more than one page.
        It maybe reported in one table or multiple tables where you
        would have to take all into account.
        Extract the balance sheet as JSON, where the first object is "Years" as key 
        and values being an array of years for which data is reported. 
        The number of years available sets the fixed length of all the following arrays.
        The second and all the proceeding keys will be the account or items reported in the 
        balance sheet, each paired with the value as an array of fixed length that includes 
        the numbers reported for that account for the corresponding year.
        The values may have commas in them, remove the commas and convert them to numbers.
        Wherever no number is reported insert an empty string. 
        If you come across a category heading, include it as a key with the value being an array 
        of the same lengths as all the other arrays that includes the blank string repeated.
        For all the accounts that are subcategories to a category heading, insert 3 spaces
        before the account name in the key. For sub-subcategories insert 3 more spaces and so on.
        If you find columns that only include percentage values ignore those.
        If you come across a row with first cell empty but it includes numbers, 
        then it must be a sum and use your knowledge of finance and give the key 
        a meaningful finance title like "Total Current Assets" or "Total Liabilities".
        Check that all keys are meaningful words that make sense in an balance sheet,
        if they are not, fix them to the closest word that makes sense, for example if you see "Uti l i ties"
        you can reason that it must be "Utilities" or if you see "Professjonal  fees" you can reason
        that that it must be "Professional fees" and make the correction.
        If there are any visible gaps between the table rows, insert "Gap1" 
        (and "Gap2", etc if there are more) as key and empty strings inside the array.
        Meticulously continue until you have accurately captured every single piece of data 
        in the balance sheet. No row should be missing from your result.
        Do not put any explaination, only output the raw json output. 
        Do not prefix with any text such as json or put any quotations around the values. 
        Format the JSON like this example:
        {
            "Years" : [2022, 2023, 2024],
            "Current Assets" : ["", "", ""],
            "Cash" : [number, number, number],
            "Accounts Recievable" : [number, number, number]     
        }
        
        If you have thoroughly searched the document and find
        no balance sheet or a table that resembles an balance sheet
        return a json like this
        {
            "Not Found" : "Balance Sheet"
        }
        Return only valid JSON.
        Go back and check that each value is an array with the length equal
        to the number of years reported. If a value is an array with fewer
        objects, add few empty strings to bring the legnth of the array to
        the fixed length that we expect for all arrays.
"""

CASH_FLOW_STATEMENT_PROMPT = """
        Analyze the file and carefully look for the cash flow statement. This maybe on one
        or more than one page. It maybe reported in one table or multiple tables where you
        would have to take all into account.
        Extract the cash flow statement as JSON, where the first object is "Years" as key 
        and values being an array of years for which data is reported. 
        The number of years available sets the fixed length of all the following arrays.
        The second and all the proceeding keys will be the account or items reported in the 
        cash flow statement, each paired with the value as an array of fixed length that includes 
        the numbers reported for that account for the corresponding year.
        The values may have commas in them, remove the commas and convert them to numbers.
        Wherever no number is reported insert an empty string. 
        If you come across a category heading, include it as a key with the value being an array 
        of the same lengths as all the other arrays that includes the blank string repeated.
        For all the accounts that are subcategories to a category heading, insert 3 spaces
        before the account name in the key. For sub-subcategories insert 3 more spaces and so on.
        If you find columns that only include percentage values ignore those.
        If you come across a row with first cell empty but it includes numbers, 
        then it must be a sum and use your knowledge of finance and give the key 
        a meaningful finance title like "Total Current Assets" or "Total Liabilities".
        Check that all keys are meaningful words that make sense in an cash flow statement,
        if they are not, fix them to the closest word that makes sense, for example if you see "Uti l i ties"
        you can reason that it must be "Utilities" or if you see "Professjonal  fees" you can reason
        that that it must be "Professional fees" and make the correction.
        If there are any visible gaps between the table rows, insert "Gap1" 
        (and "Gap2", etc if there are more) as key and empty strings inside the array.
        Meticulously continue until you have accurately captured every single piece of data 
        in the cash flow statement. No row should be missing from your result.
        Do not put any explaination, only output the raw json output. 
        Do not prefix with any text such as json or put any quotations around the values. 
        Format the JSON like this example:
        {
            "Years" : [2022, 2023, 2024],
            "Cash and cash equivalents, beginning of the year" : [number, number, number],
            "Activity" : ["", "", ""],
            "Cash Generated by Operating Activities" : [number, number, number],
            "Cash Used in Investing Activities" : [number, number, number],
            "Increase / Decrease in Cash and Cash Equivalents, beginning of the year" : [number, number, number],
            "Cash and Cash Equivalents, End of Year" : [number, number, number]     
        }
        
        If you have thoroughly searched the document and find
        no cash flow statement or a table that resembles an cash flow statement
        return a json like this
        {
            "Not Found" : "Cash flow Statement"
        }
        Return only valid JSON.
        Go back and check that each value is an array with the length equal
        to the number of years reported. If a value is an array with fewer
        objects, add few empty strings to bring the legnth of the array to
        the fixed length that we expect for all arrays.
"""

ADJUSTMENTS_PROMPT = """
        Analyze the file and carefully look for a financial table that
        maybe titled EBITDA Normalization or EBITDA Adjustments or Addbacks or
        Seller's Discretionary Earnings(SDE) or something along these lines. 
        This maybe on one or more than one page. It maybe reported in one table
        or multiple tables where you would have to take all into account.
        Extract the adjustments as JSON, where the first object is "Years" as key 
        and values being an array of years for which data is reported. 
        The number of years available sets the fixed length of all the following arrays.
        The second and all the proceeding keys will be the account or items reported in the 
        this table, each paired with the value as an array of fixed length that includes 
        the numbers reported for that account for the corresponding year.
        Wherever no number is reported insert an empty string. 
        The values may have commas in them, remove the commas and convert them to numbers.
        If you come across a category heading include it as a key with the value being an array 
        of the same lengths as all the other arrays that includes the blank string repeated.
        For all the accounts that are subcategories to a category heading, insert 3 spaces
        before the account name in the key. For sub-subcategories insert 3 more spaces and so on.
        If you find columns that only include percentage values ignore those.
        If you come across a row with first cell empty but it includes numbers, 
        then it must be a sum and use your knowledge of finance and give the key 
        a meaningful finance title like "Total Addbacks" or "Total Adjustments".
        Check that all keys are meaningful words that make sense in such a table,
        if they are not, fix them to the closest word that makes sense, for example if you see "Mea ls"
        you can reason that it must be "Meals" or if you see "Professjonal  fees" you can reason
        that that it must be "Professional fees" and make the correction.
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
        
        If you have thoroughly searched the document and find
        no income statement or a table that resembles an income statement
        return a json like this
        {
            "Not Found" : "Income Statement"
        }
        Return only valid JSON.
        Go back and check that each value is an array with the length equal
        to the number of years reported. If a value is an array with fewer
        objects, add few empty strings to bring the legnth of the array to
        the fixed length that we expect for all arrays.
"""

SUMMARY_PROMPT = """
Extract a summarized version of the income statement and balance sheet as JSON including only these line items:
years, revenue, cogs, gross margin, operating expenses, ebit (earnings before interest and tax), interest paid, taxes, net income (ebit - interest paid - taxes), sde (seller's discretionary earnings),;
cash, accounts receivable, inventory, current assets, accounts payable, current liabilities, total assets, total liabilities, total shareholder's equity;
number of employees.
The first dictionary is "Years" as key and values being an array of years for which data is reported. 
The number of years available sets the fixed length of all the following arrays.
The second and all the proceeding keys will be the account or line items reported.
Only extract these entries and do not extract any other data. 
The values may have commas in them, remove the commas and convert them to numbers.
If a value does not exist, try to calculate it from what's given, for example: 
if you have current assets and current liabilities, you can calculate total assets. 
if you have total assets and total liabilities, you can calculate total shareholder's equity.
if you have ebit, interest paid, and taxes, you can calculate net income.
if you have net income, addbacks, and owner's salary, you can calculate sde.
if you have cash, accounts receivable, and inventory, you can calculate current assets.
if you do not have a value, insert an empty string.
Do not put any explanation, only output the raw JSON output. 
Do not prefix with any text such as 'json' or put any quotations around the values.
The final results should look like this, yet with the right values: 

{
    "Years" : [number, number, number],
    "Revenue" : [number, number, number],
    "COGS" : [number, number, number],
    "Gross Margin" : [number, number, number],
    "Operating Expenses" : [number, number, number],
    "EBIT" : [number, number, number],
    "Interest Paid" : [number, number, number],
    "Taxes" : [number, number, number],
    "Net Income" : [number, number, number],
    "SDE" : [number, number, number],
    "Number of Employees" : [number, number, number],
    "Cash" : [number, number, number],
    "Accounts Receivable" : [number, number, number],
    "Inventory" : [number, number, number],
    "Current Assets" : [number, number, number],
    "Total Assets" : [number, number, number],
    "Accounts Payable" : [number, number, number],
    "Current Liabilities" : [number, number, number], 
    "Total Liabilites" : [number, number, number],
    "Total Shareholders' Equity" : [number, number, number]
}

For these items, the line item maybe a category header with no values. You might have to add up the sub-category items to arrive at the total value:
COGS, Operating Expenses, Current Assets, Current Liabilities, Total Shareholders' Equity, Total Assets, Total Liabilites

Return only a valid josn.
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
