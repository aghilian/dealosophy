# financial_analysis.py
import json
import math

def round_to_significant_digits(number, significant_digits=3):
    """Rounds a number to the specified number of significant digits."""
    if number == 0:
        return 0
    return round(number, significant_digits - int(math.floor(math.log10(abs(number)))) - 1)

def calculate_financial_metrics(summary_data):
    """Calculates financial metrics from summary.json data."""

    years = summary_data["Years"]
    num_years = len(years)
    results = {"Years": years}

    # Helper function to get values, handling missing keys and blank values
    def get_values(key):
        return summary_data.get(key, [""] * num_years)

    revenue = get_values("Revenue")
    cogs = get_values("COGS")
    gross_margin = get_values("Gross Margin")
    operating_expenses = get_values("Operating Expenses")
    ebit = get_values("EBIT")
    interest_paid = get_values("Interest Paid")
    taxes = get_values("Taxes")
    net_income = get_values("Net Income")
    cash = get_values("Cash")
    accounts_receivable = get_values("Accounts Receivable")
    inventory = get_values("Inventory")
    current_assets = get_values("Current Assets")
    accounts_payable = get_values("Accounts Payable")
    current_liabilities = get_values("Current Liabilities")
    total_liabilities = get_values("Total Liabilites")
    total_assets = get_values("Total Assets")
    total_equity = get_values("Total Equity")
    num_employees = get_values("Number of Employees")
    sde = get_values("SDE")

    for i in range(num_years):
        # Revenue Growth Rate
        if i > 0 and isinstance(revenue[i], (int, float)) and isinstance(revenue[i - 1], (int, float)) and revenue[i-1]!=0:
            results.setdefault("Revenue Growth Rate", []).append(round_to_significant_digits(((revenue[i] - revenue[i - 1]) / revenue[i - 1]) * 100))
        else:
            results.setdefault("Revenue Growth Rate", []).append("")

        # Revenue Fluctuation (%)
        if isinstance(revenue[i],(int, float)) and i>0 and isinstance(revenue[i-1],(int, float)) and revenue[i-1]!=0:
            results.setdefault("Revenue Fluctuation (%)", []).append(round_to_significant_digits(abs((revenue[i]-revenue[i-1])/revenue[i-1])*100))
        else:
            results.setdefault("Revenue Fluctuation (%)", []).append("")

        # Gross Margin
        if isinstance(revenue[i], (int, float)) and isinstance(cogs[i], (int, float)) and revenue[i] != 0:
            results.setdefault("Gross Margin", []).append(round_to_significant_digits(((revenue[i] - cogs[i]) / revenue[i]) * 100))
        else:
            results.setdefault("Gross Margin", []).append("")

        # Gross Margin Expansion
        if i > 0 and isinstance(gross_margin[i], (int, float)) and isinstance(gross_margin[i - 1], (int, float)):
            results.setdefault("Gross Margin Expansion", []).append(round_to_significant_digits(gross_margin[i] - gross_margin[i - 1]))
        else:
            results.setdefault("Gross Margin Expansion", []).append("")

        # Net Margin
        if isinstance(revenue[i], (int, float)) and isinstance(net_income[i], (int, float)) and revenue[i] != 0:
            results.setdefault("Net Margin", []).append(round_to_significant_digits((net_income[i] / revenue[i]) * 100))
        else:
            results.setdefault("Net Margin", []).append("")

        # Net Income Growth Rate
        if i > 0 and isinstance(net_income[i], (int, float)) and isinstance(net_income[i - 1], (int, float)) and net_income[i-1]!=0:
            results.setdefault("Net Income Growth Rate", []).append(round_to_significant_digits(((net_income[i] - net_income[i - 1]) / net_income[i - 1]) * 100))
        else:
            results.setdefault("Net Income Growth Rate", []).append("")

        # Inventory Turnover Per Year
        if isinstance(cogs[i], (int, float)) and isinstance(inventory[i], (int, float)) and inventory[i]!=0:
            results.setdefault("Inventory Turnover Per Year", []).append(round_to_significant_digits(cogs[i] / inventory[i]))
        else:
            results.setdefault("Inventory Turnover Per Year", []).append("")

        # Days to Turn Inventory
        if isinstance(inventory[i], (int, float)) and isinstance(cogs[i], (int, float)) and cogs[i]!=0:
            results.setdefault("Days to Turn Inventory", []).append(round_to_significant_digits((inventory[i] / cogs[i]) * 365))
        else:
            results.setdefault("Days to Turn Inventory", []).append("")

        # Days Sales Outstanding (DSO)
        if isinstance(accounts_receivable[i], (int, float)) and isinstance(revenue[i], (int, float)) and revenue[i]!=0:
            results.setdefault("Days Sales Outstanding (DSO)", []).append(round_to_significant_digits((accounts_receivable[i] / revenue[i]) * 365))
        else:
            results.setdefault("Days Sales Outstanding (DSO)", []).append("")

        # Days in Payables
        if isinstance(accounts_payable[i], (int, float)) and isinstance(cogs[i], (int, float)) and cogs[i]!=0:
            results.setdefault("Days in Payables", []).append(round_to_significant_digits((accounts_payable[i] / cogs[i]) * 365))
        else:
            results.setdefault("Days in Payables", []).append("")

        # Interest Coverage Ratio
        if isinstance(ebit[i], (int, float)) and isinstance(interest_paid[i], (int, float)) and interest_paid[i]!=0:
            results.setdefault("Interest Coverage Ratio", []).append(round_to_significant_digits(ebit[i] / interest_paid[i]))
        else:
            results.setdefault("Interest Coverage Ratio", []).append("")

        # Current Ratio
        if isinstance(current_assets[i], (int, float)) and isinstance(current_liabilities[i], (int, float)) and current_liabilities[i]!=0:
            results.setdefault("Current Ratio", []).append(round_to_significant_digits(current_assets[i] / current_liabilities[i]))
        else:
            results.setdefault("Current Ratio", []).append("")

        # Acid Test Ratio
        if isinstance(current_assets[i], (int, float)) and isinstance(inventory[i], (int, float)) and isinstance(current_liabilities[i], (int, float)) and current_liabilities[i]!=0:
            results.setdefault("Acid Test Ratio", []).append(round_to_significant_digits((current_assets[i] - inventory[i]) / current_liabilities[i]))
        else:
            results.setdefault("Acid Test Ratio", []).append("")

        # Debt-to-Equity Ratio
        if isinstance(total_liabilities[i], (int, float)) and isinstance(total_equity[i], (int, float)) and total_equity[i]!=0:
            results.setdefault("Debt-to-Equity Ratio", []).append(round_to_significant_digits(total_liabilities[i] / total_equity[i]))
        else:
            results.setdefault("Debt-to-Equity Ratio", []).append("")

        # Return on Equity (ROE)
        if isinstance(net_income[i], (int, float)) and isinstance(total_equity[i], (int, float)) and total_equity[i]!=0:
            results.setdefault("Return on Equity (ROE)", []).append(round_to_significant_digits((net_income[i] / total_equity[i]) * 100))
        else:
            results.setdefault("Return on Equity (ROE)", []).append("")

        # RoR on Total Assets
        if isinstance(net_income[i], (int, float)) and isinstance(total_assets[i], (int, float)) and total_assets[i]!=0:
            results.setdefault("RoR on Total Assets", []).append(round_to_significant_digits((net_income[i] / total_assets[i]) * 100))
        else:
            results.setdefault("RoR on Total Assets", []).append("")

        # Effective Tax Rate
        pretax_income = ebit[i] - interest_paid[i] if isinstance(ebit[i], (int, float)) and isinstance(interest_paid[i], (int, float)) else None

        if isinstance(taxes[i], (int, float)) and isinstance(pretax_income, (int, float)) and pretax_income!=0:
            results.setdefault("Effective Tax Rate", []).append(round_to_significant_digits((taxes[i] / pretax_income) * 100))
        else:
            results.setdefault("Effective Tax Rate", []).append("")

        # Revenue per employee
        if isinstance(revenue[i], (int, float)) and isinstance(num_employees[i], (int, float)) and num_employees[i]!=0:
            results.setdefault("Revenue per employee", []).append(round_to_significant_digits(revenue[i] / num_employees[i]))
        else:
            results.setdefault("Revenue per employee", []).append("")

        # Net Income per employee
        if isinstance(net_income[i], (int, float)) and isinstance(num_employees[i], (int, float)) and num_employees[i]!=0:
            results.setdefault("Net Income per employee", []).append(round_to_significant_digits(net_income[i] / num_employees[i]))
        else:
            results.setdefault("Net Income per employee", []).append("")
        # SDE multiple
        if isinstance(sde[i], (int, float)) and isinstance(ebit[i], (int, float)) and ebit[i]!=0:
            results.setdefault("SDE multiple", []).append(round_to_significant_digits(sde[i] / ebit[i]))
        else:
            results.setdefault("SDE multiple", []).append("")

    return results

# # Main execution
# if __name__ == "__main__":
#     input_filename = "summary.json"
#     output_filename = "analysis.json"

    try:
        with open(input_filename, "r") as f:
            summary_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_filename} not found.")
        exit()
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_filename}.")
        exit()

    analysis_results = calculate_financial_metrics(summary_data)

    with open(output_filename, "w") as outfile:
        json.dump(analysis_results, outfile, indent=4)

    print(f"Financial analysis results written to {output_filename}")