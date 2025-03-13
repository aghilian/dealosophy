import json
import math

def round_to_significant_digits(number, significant_digits=3):
    """Rounds a number to the specified number of significant digits."""
    if number == 0:
        return 0
    return round(number, significant_digits - int(math.floor(math.log10(abs(number)))) - 1)

def vertical_analysis(income_statement):
    """
    Performs vertical analysis on an income statement.

    Args:
        income_statement: A dictionary representing the income statement.

    Returns:
        A dictionary representing the vertical analysis results.
    """

    years = income_statement["Years"]
    num_years = len(years)

    # Find the top line (first row after "Years")
    top_line_key = list(income_statement.keys())[1]
    top_line_values = income_statement[top_line_key]

    vertical_analysis_results = {"Years": years}
    vertical_analysis_results[top_line_key] = [100.0] * num_years

    for key, values in income_statement.items():
        if key == "Years" or key == top_line_key:
            continue

        percentage_values = []
        for i in range(num_years):
            if isinstance(values[i], (int, float)):
                if top_line_values[i] != 0:
                    percentage = (values[i] / top_line_values[i]) * 100
                    rounded_percentage = round_to_significant_digits(percentage)
                    percentage_values.append(rounded_percentage)
                else:
                    percentage_values.append(0)
            else:
                percentage_values.append("")

        vertical_analysis_results[key] = percentage_values

    return vertical_analysis_results

# Read income_statement.json
try:
    with open("income_statement.json", "r") as f:
        income_statement = json.load(f)
except FileNotFoundError:
    print("Error: income_statement.json not found.")
    exit()
except json.JSONDecodeError:
    print("Error: Invalid JSON format in income_statement.json.")
    exit()

# Perform vertical analysis
vertical_analysis_results = vertical_analysis(income_statement)

# Create output filename
input_filename = "income_statement.json"
output_filename = input_filename.replace(".json", "_vertical.json")

# Write results to output file
with open(output_filename, "w") as outfile:
    json.dump(vertical_analysis_results, outfile, indent=4)

print(f"Vertical analysis results written to {output_filename}")