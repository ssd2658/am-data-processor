import pandas as pd
import PyPDF2
from pathlib import Path
import json
import os
import re
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from utils.logger_config import processor_logger as logger

# Load environment variables
load_dotenv()

class DocumentProcessor:
    def __init__(self):
        logger.info("Initializing DocumentProcessor")
        self.client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Define the extraction prompt
        self.extraction_prompt = """
        You are a financial data extraction expert. Analyze the following mutual fund portfolio data and extract ALL holdings and sector information.
        The data represents a mutual fund's portfolio holdings, but the exact column names and structure may vary.

        First, analyze the Column Mapping Analysis section to understand the data structure.
        Then, process the Complete Portfolio Data section to extract ALL records - it's crucial to include every holding and sector.

        Format the output as a JSON object with this structure:

        {
            "fund_info": {
                "name": "Extract from sheet name or relevant column",
                "id": "Look for fund identifier or code",
                "type": "Determine fund type from available data",
                "aum": Calculate total portfolio value if market values are available,
                "currency": "Determine from market value format, default to INR for Indian funds"
            },
            "holdings": [
                {
                    "stock_name": "Map from Security Name or similar column",
                    "isin": "Map from ISIN or similar identifier column",
                    "sector": "Map from Industry/Sector column if available",
                    "percentage": "Map from percentage/proportion column or calculate if possible",
                    "value": "Map from market value/amount column"
                }
                // Include ALL holdings from the data, do not limit the number of records
            ],
            "sector_allocation": [
                {
                    "name": "Industry/Sector name",
                    "total_value": "Sum of market values for the sector",
                    "percentage_holding": "Calculate from total value",
                    "number_of_stocks": "Count of stocks in this sector",
                    "companies": ["ALL ISINs in this sector"],
                    "allocation": "Sector's percentage of total portfolio"
                }
                // Include ALL sectors from the data, do not limit the number of records
            ]
        }

        Critical Requirements:
        1. Process and include EVERY SINGLE holding and sector from the data
        2. Do not skip or limit the number of records
        3. Use the column descriptions to identify relevant fields
        4. Calculate derived values where possible
        5. Return actual numbers, not strings, for numeric values
        6. Group ALL holdings by sector/industry if such classification is available
        7. Double-check that the number of holdings matches the Total Records count provided

        Extract this information from the following text:
        """
    
    async def process_file(self, file_path):
        """Process a file and extract structured data using Claude AI"""
        try:
            # Read file content based on extension
            file_path = Path(file_path)
            content = self._read_file_content(file_path)
            logger.info("Successfully read file content")
            
            # Get response from Claude
            message = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=8096,
                temperature=0,
                system="You are a financial data extraction expert. Extract structured data from mutual fund portfolio documents.",
                messages=[
                    {
                        "role": "user",
                        "content": self.extraction_prompt + "\n\n" + content
                    }
                ]
            )
            
            # Log Claude's response
            logger.info("Received response from Claude AI")
            logger.info("Raw Claude Response:")
            print("\n" + "="*80)
            print(message.content[0].text)
            print("="*80 + "\n")

            # Parse the response
            try:
                # Extract JSON content
                response_text = message.content[0].text
                
                # Find JSON content (assuming it's within ```json ``` blocks or { })
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON content found in response")
                
                json_str = response_text[json_start:json_end]
                
                # Clean up the JSON string
                json_str = json_str.replace('```json', '').replace('```', '')
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                json_str = re.sub(r'//.*?\n', '\n', json_str)
                
                # Parse JSON
                try:
                    data = json.loads(json_str)
                    # Print formatted JSON
                    logger.info("Parsed JSON Response:")
                    print("\n" + "="*80)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print("="*80 + "\n")
                    
                    # Log statistics
                    logger.info(f"Number of holdings: {len(data.get('holdings', []))}")
                    logger.info(f"Number of sectors: {len(data.get('sector_allocation', []))}")
                    
                    if len(data.get('holdings', [])) < 10:
                        logger.warning("Warning: Less than 10 holdings found. This might indicate incomplete extraction.")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON Decode Error: {str(e)}")
                    logger.error(f"Problem section: {json_str[max(0, e.pos-50):min(len(json_str), e.pos+50)]}")
                    raise
                
                # Validate the structure
                required_keys = ['fund_info', 'holdings', 'sector_allocation']
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    raise ValueError(f"Missing required keys in response: {missing_keys}")
                
                # Extract key entities from the processed data
                entities = {
                    'fund_names': [data['fund_info']['name']],
                    'amounts': [str(data['fund_info']['aum'])],
                    'currencies': [data['fund_info']['currency']]
                }
                
                # Format holdings data
                holdings = [{'data': holding} for holding in data.get('holdings', [])]
                
                # Format sector allocation data
                sectors = [{'data': sector} for sector in data.get('sector_allocation', [])]
                
                return {
                    'raw_text': content,
                    'entities': entities,
                    'holdings': holdings,
                    'sectors': sectors,
                    'raw_data': data
                }
                
            except Exception as e:
                logger.error(f"Failed to parse Claude's response: {str(e)}", exc_info=True)
                raise
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            raise

    def _read_file_content(self, file_path):
        """Read content from different file types"""
        extension = file_path.suffix.lower()
        logger.info(f"Reading file with extension: {extension}")
        
        try:
            if extension in ['.xls', '.xlsx']:
                logger.info("Processing Excel file")
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                logger.info(f"Found {len(sheet_names)} sheets: {sheet_names}")
                
                if len(sheet_names) > 1:
                    sheet_name = sheet_names[1]
                    logger.info(f"Processing sheet: {sheet_name}")
                    
                    # Read all rows, skipping initial rows until we find the header
                    df = None
                    for skiprows in range(10):  # Try first 10 rows
                        temp_df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)
                        # Check if we found the header row (look for common column indicators)
                        if any(col.lower().strip() in ['isin', 'name', 'security', 'market'] for col in temp_df.columns):
                            df = temp_df
                            break
                    
                    if df is None:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)  # Default to no skipping
                    
                    # Drop any completely empty rows or columns
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    
                    # Create structured text description
                    text = f"Fund Portfolio Analysis\n\n"
                    text += f"Sheet Name: {sheet_name}\n\n"
                    
                    # Describe columns and their mappings
                    text += "Column Mapping Analysis:\n"
                    for col in df.columns:
                        text += f"Column: {col}\n"
                        non_null_values = df[col].dropna()
                        if len(non_null_values) > 0:
                            text += f"Data Type: {df[col].dtype}\n"
                            text += f"Sample Values: {', '.join(map(str, non_null_values.head(3)))}\n"
                            text += f"Total Non-null Values: {len(non_null_values)}\n"
                        text += "\n"
                    
                    # Add summary statistics
                    text += f"\nTotal Records: {len(df)}\n"
                    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                    for col in numeric_cols:
                        text += f"{col} Total: {df[col].sum()}\n"
                    
                    # Add the full portfolio data
                    text += "\nComplete Portfolio Data:\n"
                    # Format DataFrame string with better alignment
                    pd.set_option('display.max_rows', None)
                    pd.set_option('display.max_columns', None)
                    pd.set_option('display.width', None)
                    text += df.to_string(index=False)
                    
                    logger.info(f"Processed {len(df)} records from Excel sheet")
                    logger.debug(f"Generated text content length: {len(text)}")
                    return text
                else:
                    raise ValueError("Excel file must have at least two sheets")
                
            elif extension == '.csv':
                df = pd.read_csv(file_path)
                return df.to_string()
                
            elif extension == '.pdf':
                text = ""
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
                
            else:
                raise ValueError(f"Unsupported file type: {extension}")
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}", exc_info=True)
            raise
