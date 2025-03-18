import json
import math
import os
import logging
from uncertainties import ufloat

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def format_value(value, is_percentage=False):
    """Formats a value according to requirements:
    - 3 significant digits
    - Negative numbers with negative sign
    - Percentages with % sign in front
    - Comma separators for thousands
    """
    try:
        if not isinstance(value, (int, float)):
            return ""
        
        # Round to appropriate decimal places
        if abs(value) >= 100:
            formatted = f"{value:,.0f}"  # Add comma separator with no decimals
        elif abs(value) >= 10:
            formatted = f"{value:,.1f}"  # Add comma separator with 1 decimal
        else:
            formatted = f"{value:,.2f}"  # Add comma separator with 2 decimals
        
        # Format as percentage if required
        if is_percentage:
            return f"{formatted}%"
        
        return formatted
    except Exception as e:
        logging.error(f"Error formatting value {value}: {e}")
        return ""

def calculate_financial_metrics(summary_data):
    """Calculates financial metrics from summary data."""
    try:
        years = summary_data["Years"]
        num_years = len(years)
        results = {"Years": years}
        logging.info(f"Processing {num_years} years of data: {years}")
        
        # Log the raw input data
        logging.info(f"Input summary data: {json.dumps(summary_data, indent=2)}")

        # Helper function to get values, handling missing keys and blank values
        def get_values(key):
            values = summary_data.get(key, [""] * num_years)
            # Add detailed logging for each metric's raw values
            logging.info(f"Raw values for {key}: {values}")
            # Convert string numbers to float if possible
            try:
                # Convert empty strings or None to 0, otherwise convert to float
                values = [float(v) if v not in ["", None] else 0 for v in values]
            except ValueError:
                logging.error(f"Could not convert values for {key} to float: {values}")
            logging.info(f"Processed values for {key}: {values}")
            return values

        # Get all required values with detailed logging
        metrics = {
            "Revenue": get_values("Revenue"),
            "COGS": get_values("COGS"),
            "Gross Margin": get_values("Gross Margin"),
            "Operating Expenses": get_values("Operating Expenses"),
            "EBIT": get_values("EBIT"),
            "Interest Paid": get_values("Interest Paid"),
            "Taxes": get_values("Taxes"),  # This will now convert empty strings to 0
            "Net Income": get_values("Net Income"),
            "Cash": get_values("Cash"),
            "Accounts Receivable": get_values("Accounts Receivable"),
            "Inventory": get_values("Inventory"),
            "Current Assets": get_values("Current Assets"),
            "Accounts Payable": get_values("Accounts Payable"),
            "Current Liabilities": get_values("Current Liabilities"),
            "Total Liabilities": get_values("Total Liabilities"),  # Fixed typo here
            "Total Assets": get_values("Total Assets"),
            "Total Equity": get_values("Total Equity"),
            "Number of Employees": get_values("Number of Employees"),
            "SDE": get_values("SDE")
        }

        logging.info("Processed metrics data:")
        for key, value in metrics.items():
            logging.info(f"{key}: {value}")

        for i in range(num_years):
            logging.info(f"\nProcessing year {years[i]}")
            try:
                # Process each metric with error handling
                def safe_calculate(metric_name, calculation, is_percentage=False):
                    try:
                        result = calculation()
                        if result is None:
                            logging.warning(f"{metric_name} calculation returned None")
                            results.setdefault(metric_name, []).append("")
                            return
                            
                        formatted_result = format_value(result, is_percentage)
                        results.setdefault(metric_name, []).append(formatted_result)
                        logging.info(f"Successfully calculated {metric_name} for {years[i]}: {formatted_result}")
                    except Exception as e:
                        logging.error(f"Error calculating {metric_name} for {years[i]}: {e}")
                        logging.error(f"Values used in calculation: {[metrics[k][i] if k in metrics else 'Missing' for k in calculation.__code__.co_names if k in metrics]}")
                        results.setdefault(metric_name, []).append("")

                # Revenue Growth Rate
                safe_calculate(
                    "Revenue Growth Rate (%)",
                    lambda: ((metrics["Revenue"][i] - metrics["Revenue"][i-1]) / metrics["Revenue"][i-1] * 100) if i > 0 and isinstance(metrics["Revenue"][i], (int, float)) and isinstance(metrics["Revenue"][i-1], (int, float)) and metrics["Revenue"][i-1] != 0 else None,
                    True
                )

                # Gross Margin
                safe_calculate(
                    "Gross Margin (%)",
                    lambda: ((metrics["Revenue"][i] - metrics["COGS"][i]) / metrics["Revenue"][i] * 100) if isinstance(metrics["Revenue"][i], (int, float)) and isinstance(metrics["COGS"][i], (int, float)) and metrics["Revenue"][i] != 0 else None,
                    True
                )

                # Gross Margin Expansion
                safe_calculate(
                    "Gross Margin Expansion (%)",
                    lambda: ((metrics["Gross Margin"][i] - metrics["Gross Margin"][i-1]) / metrics["Gross Margin"][i-1] * 100) if i > 0 and isinstance(metrics["Gross Margin"][i], (int, float)) and isinstance(metrics["Gross Margin"][i-1], (int, float)) and metrics["Gross Margin"][i-1] != 0 else None,
                    True
                )

                # Net Margin
                safe_calculate(
                    "Net Margin (%)",
                    lambda: ((metrics["Net Income"][i] / metrics["Revenue"][i]) * 100) if isinstance(metrics["Net Income"][i], (int, float)) and isinstance(metrics["Revenue"][i], (int, float)) and metrics["Revenue"][i] != 0 else None,
                    True
                )

                # Net Income Growth Rate
                safe_calculate(
                    "Net Income Growth Rate (%)",
                    lambda: ((metrics["Net Income"][i] - metrics["Net Income"][i-1]) / metrics["Net Income"][i-1] * 100) if i > 0 and isinstance(metrics["Net Income"][i], (int, float)) and isinstance(metrics["Net Income"][i-1], (int, float)) and metrics["Net Income"][i-1] != 0 else None,
                    True
                )

                # Inventory Turnover Per Year
                safe_calculate(
                    "Inventory Turnover Per Year",
                    lambda: (metrics["COGS"][i] / metrics["Inventory"][i]) if isinstance(metrics["COGS"][i], (int, float)) and isinstance(metrics["Inventory"][i], (int, float)) and metrics["Inventory"][i] != 0 else None
                )

                # Days to Turn Inventory
                safe_calculate(
                    "Days to Turn Inventory (Days)",
                    lambda: ((metrics["Inventory"][i] / metrics["COGS"][i]) * 365) if isinstance(metrics["Inventory"][i], (int, float)) and isinstance(metrics["COGS"][i], (int, float)) and metrics["COGS"][i] != 0 else None
                )

                # Days Sales Outstanding (DSO)
                safe_calculate(
                    "Days Sales Outstanding (DSO) (Days)",
                    lambda: ((metrics["Accounts Receivable"][i] / metrics["Revenue"][i]) * 365) if isinstance(metrics["Accounts Receivable"][i], (int, float)) and isinstance(metrics["Revenue"][i], (int, float)) and metrics["Revenue"][i] != 0 else None
                )

                # Days in Payables
                safe_calculate(
                    "Days in Payables (Days)",
                    lambda: ((metrics["Accounts Payable"][i] / metrics["COGS"][i]) * 365) if isinstance(metrics["Accounts Payable"][i], (int, float)) and isinstance(metrics["COGS"][i], (int, float)) and metrics["COGS"][i] != 0 else None
                )

                # Interest Coverage Ratio
                safe_calculate(
                    "Interest Coverage Ratio",
                    lambda: (metrics["EBIT"][i] / metrics["Interest Paid"][i]) if isinstance(metrics["EBIT"][i], (int, float)) and isinstance(metrics["Interest Paid"][i], (int, float)) and metrics["Interest Paid"][i] != 0 else None
                )

                # Current Ratio
                safe_calculate(
                    "Current Ratio",
                    lambda: (metrics["Current Assets"][i] / metrics["Current Liabilities"][i]) if isinstance(metrics["Current Assets"][i], (int, float)) and isinstance(metrics["Current Liabilities"][i], (int, float)) and metrics["Current Liabilities"][i] != 0 else None
                )

                # Acid Test Ratio
                safe_calculate(
                    "Acid Test Ratio",
                    lambda: ((metrics["Current Assets"][i] - metrics["Inventory"][i]) / metrics["Current Liabilities"][i]) if isinstance(metrics["Current Assets"][i], (int, float)) and isinstance(metrics["Inventory"][i], (int, float)) and isinstance(metrics["Current Liabilities"][i], (int, float)) and metrics["Current Liabilities"][i] != 0 else None
                )

                # Debt-to-Equity Ratio
                safe_calculate(
                    "Debt-to-Equity Ratio",
                    lambda: (metrics["Total Liabilities"][i] / metrics["Total Equity"][i]) if isinstance(metrics["Total Liabilities"][i], (int, float)) and isinstance(metrics["Total Equity"][i], (int, float)) and metrics["Total Equity"][i] != 0 else None
                )

                # Return on Equity (ROE)
                safe_calculate(
                    "Return on Equity (ROE)",
                    lambda: ((metrics["Net Income"][i] / metrics["Total Equity"][i]) * 100) if isinstance(metrics["Net Income"][i], (int, float)) and isinstance(metrics["Total Equity"][i], (int, float)) and metrics["Total Equity"][i] != 0 else None,
                    True
                )

                # RoR on Total Assets
                safe_calculate(
                    "RoR on Total Assets",
                    lambda: ((metrics["Net Income"][i] / metrics["Total Assets"][i]) * 100) if isinstance(metrics["Net Income"][i], (int, float)) and isinstance(metrics["Total Assets"][i], (int, float)) and metrics["Total Assets"][i] != 0 else None,
                    True
                )

                # Effective Tax Rate
                pretax_income = metrics["EBIT"][i] - metrics["Interest Paid"][i] if isinstance(metrics["EBIT"][i], (int, float)) and isinstance(metrics["Interest Paid"][i], (int, float)) else None
                safe_calculate(
                    "Effective Tax Rate (%)",
                    lambda: ((metrics["Taxes"][i] / pretax_income) * 100) if isinstance(metrics["Taxes"][i], (int, float)) and isinstance(pretax_income, (int, float)) and pretax_income != 0 else None,
                    True
                )

                # Revenue per employee
                safe_calculate(
                    "Revenue per employee ($)",
                    lambda: (metrics["Revenue"][i] / metrics["Number of Employees"][i]) if isinstance(metrics["Revenue"][i], (int, float)) and isinstance(metrics["Number of Employees"][i], (int, float)) and metrics["Number of Employees"][i] != 0 else None
                )

                # Net Income per employee
                safe_calculate(
                    "Net Income per employee ($)",
                    lambda: (metrics["Net Income"][i] / metrics["Number of Employees"][i]) if isinstance(metrics["Net Income"][i], (int, float)) and isinstance(metrics["Number of Employees"][i], (int, float)) and metrics["Number of Employees"][i] != 0 else None
                )

                # SDE multiple
                safe_calculate(
                    "SDE/EBIT multiple",
                    lambda: (metrics["SDE"][i] / metrics["EBIT"][i]) if isinstance(metrics["SDE"][i], (int, float)) and isinstance(metrics["EBIT"][i], (int, float)) and metrics["EBIT"][i] != 0 else None
                )

            except Exception as e:
                logging.error(f"Error processing year {years[i]}: {e}")
                continue

        return results
    except Exception as e:
        logging.error(f"Error in calculate_financial_metrics: {e}")
        raise

def analyze_json_file(json_file_path):
    """
    Process a JSON file with financial data and save analysis results.
    
    Args:
        json_file_path (str): Path to the JSON file to analyze
        
    Returns:
        str: Path to the created analysis file or None if failed
    """
    try:
        # Extract directory and create output path
        file_dir = os.path.dirname(json_file_path)
        output_path = os.path.join(file_dir, "analysis.json")
        
        logging.info(f"🔍 Analyzing financial data from: {json_file_path}")
        
        # Load the input JSON file
        with open(json_file_path, "r") as f:
            summary_data = json.load(f)
            logging.debug(f"Loaded summary data: {json.dumps(summary_data, indent=2)}")
            
        # Calculate metrics
        analysis_results = calculate_financial_metrics(summary_data)
        
        # Verify results before writing
        logging.debug(f"Analysis results to be written: {json.dumps(analysis_results, indent=2)}")
        
        # Write results to output file
        with open(output_path, "w") as outfile:
            json.dump(analysis_results, outfile, indent=4)
            outfile.flush()  # Ensure all data is written
            os.fsync(outfile.fileno())  # Force write to disk
            
        logging.info(f"✅ Financial analysis results written to: {output_path}")
        
        # Verify the written file
        with open(output_path, "r") as f:
            written_data = json.load(f)
            if written_data == analysis_results:
                logging.info("✅ File verification successful")
            else:
                logging.error("❌ File verification failed - content mismatch")
        
        return output_path
        
    except FileNotFoundError:
        logging.error(f"❌ Error: Input file {json_file_path} not found.")
        return None
    except json.JSONDecodeError as je:
        logging.error(f"❌ Error: Invalid JSON format in {json_file_path}: {je}")
        return None
    except Exception as e:
        logging.error(f"❌ Error during financial analysis: {str(e)}")
        return None