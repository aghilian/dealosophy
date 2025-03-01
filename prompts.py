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


COMPANY_INFO_PROMPT = """
Extract the following information in this exact order about the company 
and if the information is unknown put null: 
Company's Name, Asking price, Years in Business, Owner Name(s), Number of employees, Employee Info Summary, 
What does this business do in less than 20 words, What industry or industries is this business in, Business Address, facilities ownership type, lease per month rent, lease
renewal status briefly, location size in sqaure feet.
Do not put any explaination, only output the raw json output. Do not prefix with any text such as json or put any quotations around the values.
Output the information into a JSON Object in the following format.
{
        "Name": string,
        "Asking price": number,
        "Years in business": number,
        "Owner(s)": string,
        "Number of employees" : number,
        "Employees", string,
        "Business info": string,
        "Industry" : string,
        "Address" : string,
        "Facilities ownership type": string,
        "Lease per month rent": number,
        "Lease expiry and renewal status": string,
        "Location size in Sqare feet": number          
    }
}
You may need to calculate the "Lease per month rent". For example multiplying facilities area
by rent per sq ft. 
"""

BROKER_INFO_PROMPT = """
Extract the following information about the broker and if the information is unknown put null: 
Brokerage firm, Broker Agent, Broker agent phone number, broker agent email.
 Do not put any explaination, only output the raw json output. Do not prefix with any text such as json or put any quotations around the values.
 Output the information into a JSON Object in the following format.
 {

    "Brokerage firm": string,
    "Broker Agent": string,
    "Broker phone": string,
    "Broker email" : string
    
}    
"""

