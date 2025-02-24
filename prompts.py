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
            "Not Found" : ""
        }
        Return only valid JSON.
        Go back and check that each value is an array with the length equal
        to the number of years reported. If a value is an array with fewer
        objects, add few empty strings to bring the legnth of the array to
        the fixed length that we expect for all arrays.
"""

BALANCE_SHEET_PROMPT = """
    <<YOUR DETAILED BALANCE SHEET EXTRACTION PROMPT HERE>>
"""

CASH_FLOW_STATEMENT_PROMPT = """
    <<YOUR DETAILED CASH FLOW STATEMENT EXTRACTION PROMPT HERE>>
"""