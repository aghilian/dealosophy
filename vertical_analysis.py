import json

def vertical_analysis(income_statement_data):
    """
    Performs vertical analysis on an income statement.

    Args:
        income_statement_data: A python dictionary representing the income statement.

    Returns:
        A JSON string representing the vertical analysis results.
    """

    income_statement = income_statement_data
    years = income_statement["Years"]
    num_years = len(years)
    sales = income_statement[list(income_statement.keys())[1]] # get the second key's value assuming sales is always the second key.

    vertical_analysis_results = {"Years": years}

    for key, values in income_statement.items():
        if key == "Years" or key == list(income_statement.keys())[1]: #skip years and sales
            continue

        percentage_values = []
        for i in range(num_years):
            if isinstance(values[i], (int, float)):
                percentage = (values[i] / sales[i]) * 100
                percentage_values.append(percentage)
            else:
                percentage_values.append("") #keep empty strings as empty strings.

        vertical_analysis_results[key] = percentage_values

    return json.dumps(vertical_analysis_results, indent=4)

# Load JSON from file
with open("income_statement.json", "r") as f:
    income_statement_data = json.load(f)

vertical_analysis_json = vertical_analysis(income_statement_data)
print(vertical_analysis_json)