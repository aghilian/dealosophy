import json
import math
import os
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def round_to_significant_digits(number, significant_digits=3):
    """Rounds a number to the specified number of significant digits."""
    if number == 0:
        return 0
    return round(number, significant_digits - int(math.floor(math.log10(abs(number)))) - 1)

def vertical_analysis(summary_data):
    """
    Performs vertical analysis on the summary data.
    Income statement items are calculated as percentage of Revenue.
    Balance sheet items are calculated as percentage of Total Assets.
    """
    try:
        # Get years from the data
        years = summary_data["Years"]
        num_years = len(years)
        logging.info(f"Processing {num_years} years of data: {years}")

        # Initialize result dictionary with years
        result = {"Years": years}

        # Income Statement Section (as percentage of Revenue)
        revenue_values = summary_data["Revenue"]
        income_statement_items = [
            "Revenue", "COGS", "Gross Margin", "Operating Expenses",
            "EBIT", "Interest Paid", "Taxes", "Net Income", "SDE"
        ]

        for item in income_statement_items:
            values = summary_data[item]
            percentages = []
            for i in range(num_years):
                if values[i] not in ["", None] and revenue_values[i] not in ["", None]:
                    try:
                        value = float(values[i])
                        revenue = float(revenue_values[i])
                        if revenue != 0:
                            percentage = (value / revenue) * 100
                            # Ensure exactly one decimal point
                            formatted_value = f"{percentage:.1f}"
                            # Remove any trailing zeros after decimal
                            if formatted_value.endswith('.0'):
                                formatted_value = formatted_value[:-2]
                            percentages.append(formatted_value)
                        else:
                            percentages.append("")
                    except (ValueError, TypeError):
                        percentages.append("")
                else:
                    percentages.append("")
            result[item] = percentages

        # Add blank row (without label)
        result[""] = [""] * num_years

        # Balance Sheet Section (as percentage of Total Assets)
        total_assets_values = summary_data["Total Assets"]
        balance_sheet_items = [
            "Cash", "Accounts Receivable", "Inventory", "Current Assets",
            "Total Assets", "Accounts Payable", "Current Liabilities",
            "Total Liabilities", "Total Equity"
        ]

        for item in balance_sheet_items:
            values = summary_data[item]
            percentages = []
            for i in range(num_years):
                if values[i] not in ["", None] and total_assets_values[i] not in ["", None]:
                    try:
                        value = float(values[i])
                        total_assets = float(total_assets_values[i])
                        if total_assets != 0:
                            if item == "Total Equity":
                                # Calculate as 100% - Total Liabilities percentage
                                total_liabilities = float(summary_data["Total Liabilities"][i])
                                if total_assets != 0:
                                    total_liabilities_pct = (total_liabilities / total_assets) * 100
                                    percentage = 100 - total_liabilities_pct
                            else:
                                percentage = (value / total_assets) * 100
                            # Ensure exactly one decimal point
                            formatted_value = f"{percentage:.1f}"
                            # Remove any trailing zeros after decimal
                            if formatted_value.endswith('.0'):
                                formatted_value = formatted_value[:-2]
                            percentages.append(formatted_value)
                        else:
                            percentages.append("")
                    except (ValueError, TypeError):
                        percentages.append("")
                else:
                    percentages.append("")
            result[item] = percentages

        # Write results to file
        output_path = os.path.join(os.path.dirname(summary_data["file_path"]), "summary_vertical.json")
        with open(output_path, "w") as f:
            json.dump(result, f, indent=4)
        logging.info(f"✅ Vertical analysis results written to: {output_path}")

        # Verify the file was written correctly
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                verification_data = json.load(f)
                if verification_data == result:
                    logging.info("✅ File verification successful")
                    return output_path
                else:
                    logging.error("❌ File verification failed: data mismatch")
                    return None
        else:
            logging.error("❌ File verification failed: file not found")
            return None

    except Exception as e:
        logging.error(f"❌ Error during vertical analysis: {str(e)}")
        return None

def analyze_vertical(folder_path):
    """
    Process a JSON file with summary data and save vertical analysis results.
    
    Args:
        folder_path (str): Path to the folder containing summary.json
        
    Returns:
        str: Path to the created analysis file or None if failed
    """
    try:
        # Construct input and output paths
        input_path = os.path.join(folder_path, "summary.json")
        output_path = os.path.join(folder_path, "summary_vertical.json")
        
        logging.info(f"🔍 Analyzing summary data from: {input_path}")
        
        # Load the input JSON file
        with open(input_path, "r") as f:
            summary_data = json.load(f)
            logging.debug(f"Loaded summary data: {json.dumps(summary_data, indent=2)}")
            
        # Calculate vertical analysis
        analysis_results = vertical_analysis(summary_data)
        
        # Verify results before writing
        logging.debug(f"Analysis results to be written: {json.dumps(analysis_results, indent=2)}")
        
        # Write results to output file
        with open(output_path, "w") as outfile:
            json.dump(analysis_results, outfile, indent=4)
            outfile.flush()  # Ensure all data is written
            os.fsync(outfile.fileno())  # Force write to disk
            
        logging.info(f"✅ Vertical analysis results written to: {output_path}")
        
        # Verify the written file
        with open(output_path, "r") as f:
            written_data = json.load(f)
            if written_data == analysis_results:
                logging.info("✅ File verification successful")
            else:
                logging.error("❌ File verification failed - content mismatch")
        
        return output_path
        
    except FileNotFoundError:
        logging.error(f"❌ Error: Input file {input_path} not found.")
        return None
    except json.JSONDecodeError as je:
        logging.error(f"❌ Error: Invalid JSON format in {input_path}: {je}")
        return None
    except Exception as e:
        logging.error(f"❌ Error during vertical analysis: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    folder_path = r"C:\dealosophy\users\iman@opensails.ca\3\json_files"
    result = analyze_vertical(folder_path)
    if result:
        print(f"Vertical analysis completed successfully. Results saved to: {result}")
    else:
        print("Vertical analysis failed. Check the logs for details.")