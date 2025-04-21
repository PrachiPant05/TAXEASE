import re
import json

class TaxCalcAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def extract_financial_info_from_text(self, financial_text):
        """Extract financial information directly from text without using LLM"""
        financial_data = {
            "salary_income": 0,
            "other_income": 0,
            "deductions_80c": 0,
            "home_loan_principal": 0
        }
        
        if not financial_text:
            return financial_data
            
        salary_patterns = [
            r'salary\s*(?:income)?\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'annual\s*(?:income|salary)\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'gross\s*(?:income|salary)\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'total\s*(?:income|salary)\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, financial_text, re.IGNORECASE)
            if match:
                financial_data["salary_income"] = float(match.group(1).replace(',', ''))
                break
        
        # Try to find other income
        other_income_patterns = [
            r'other\s*income\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'interest\s*income\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'dividend\s*income\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'rental\s*income\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        ]
        
        for pattern in other_income_patterns:
            match = re.search(pattern, financial_text, re.IGNORECASE)
            if match:
                financial_data["other_income"] += float(match.group(1).replace(',', ''))
        
        # Try to find 80C deductions
        deduction_patterns = [
            r'80[cC]\s*(?:deduction)?\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'PF\s*(?:contribution)?\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'LIC\s*(?:premium)?\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'ELSS\s*(?:investment)?\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'PPF\s*(?:contribution)?\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        ]
        
        for pattern in deduction_patterns:
            match = re.search(pattern, financial_text, re.IGNORECASE)
            if match:
                financial_data["deductions_80c"] += float(match.group(1).replace(',', ''))
        
        # Try to find home loan principal
        home_loan_patterns = [
            r'home\s*loan\s*principal\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'principal\s*repayment\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'housing\s*loan\s*principal\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        ]
        
        for pattern in home_loan_patterns:
            match = re.search(pattern, financial_text, re.IGNORECASE)
            if match:
                financial_data["home_loan_principal"] = float(match.group(1).replace(',', ''))
                break
        
        # If no financial data is found, try using the LLM if available
        if (financial_data["salary_income"] == 0 and 
            financial_data["other_income"] == 0 and
            self.llm_client is not None):
            
            return self.extract_financial_info_from_llm(financial_text)
            
        return financial_data
    
    def extract_financial_info_from_llm(self, financial_text):
        """Extract financial information using Ollama LLM"""
        financial_data = {
            "salary_income": 0,
            "other_income": 0,
            "deductions_80c": 0,
            "home_loan_principal": 0
        }
        
        if not self.llm_client or not financial_text:
            return financial_data
            
        try:
            # Prepare the prompt for Ollama
            prompt = f"""
            Extract the following financial information from the text below:
            1. Salary income (annual)
            2. Other income (interest, dividends, capital gains, etc.)
            3. Section 80C deductions (PF, LIC, ELSS, etc.)
            4. Home loan principal repayment amount
            
            Format your response as a structured JSON object with these exact keys:
            "salary_income": [number],
            "other_income": [number],
            "deductions_80c": [number],
            "home_loan_principal": [number]
            
            Financial Text:
            {financial_text}
            """
            
            # Call Ollama to extract structured data
            response = self.llm_client.generate(
                model="llama2",
                prompt=prompt,
                temperature=0.1,  # Low temperature for more deterministic results
                max_tokens=500
            )
            
            # Parse the Ollama response to extract the values
            if response and "response" in response:
                llm_response = response["response"]
                
                # Try to extract JSON data
                try:
                    # Find JSON-like content using regex
                    json_match = re.search(r'\{[\s\S]*\}', llm_response)
                    if json_match:
                        json_str = json_match.group(0)
                        extracted_json = json.loads(json_str)
                        
                        # Update financial data with extracted values
                        if "salary_income" in extracted_json and isinstance(extracted_json["salary_income"], (int, float)):
                            financial_data["salary_income"] = float(extracted_json["salary_income"])
                        
                        if "other_income" in extracted_json and isinstance(extracted_json["other_income"], (int, float)):
                            financial_data["other_income"] = float(extracted_json["other_income"])
                        
                        if "deductions_80c" in extracted_json and isinstance(extracted_json["deductions_80c"], (int, float)):
                            financial_data["deductions_80c"] = float(extracted_json["deductions_80c"])
                        
                        if "home_loan_principal" in extracted_json and isinstance(extracted_json["home_loan_principal"], (int, float)):
                            financial_data["home_loan_principal"] = float(extracted_json["home_loan_principal"])
                            
                        return financial_data
                except Exception as json_error:
                    print(f"Failed to parse JSON from LLM response: {json_error}")
                    
                # Fallback to regex extraction if JSON parsing fails
                # Extract salary income
                salary_match = re.search(r'salary income.*?(\d+(?:,\d+)*(?:\.\d+)?)', llm_response, re.IGNORECASE)
                if salary_match:
                    financial_data["salary_income"] = float(salary_match.group(1).replace(',', ''))
                
                # Extract other income
                other_income_match = re.search(r'other income.*?(\d+(?:,\d+)*(?:\.\d+)?)', llm_response, re.IGNORECASE)
                if other_income_match:
                    financial_data["other_income"] = float(other_income_match.group(1).replace(',', ''))
                
                # Extract 80C deductions
                deductions_match = re.search(r'section 80c.*?(\d+(?:,\d+)*(?:\.\d+)?)', llm_response, re.IGNORECASE)
                if deductions_match:
                    financial_data["deductions_80c"] = float(deductions_match.group(1).replace(',', ''))
                
                # Extract home loan principal
                home_loan_match = re.search(r'home loan principal.*?(\d+(?:,\d+)*(?:\.\d+)?)', llm_response, re.IGNORECASE)
                if home_loan_match:
                    financial_data["home_loan_principal"] = float(home_loan_match.group(1).replace(',', ''))
        
        except Exception as e:
            print(f"Error using Ollama for financial data extraction: {e}")
        
        return financial_data
    
    def calculate_tax(self, extracted_data):
        """
        Main method called from the app that processes extracted data and returns tax calculations.
        """
        # Check if we have financial_text in the extracted data
        financial_text = extracted_data.get("financial_text", "")
        
        # Extract financial info from the text data
        financial_data = self.extract_financial_info_from_text(financial_text)
        
        # If we have no financial data from text extraction, try to use default values
        if financial_data["salary_income"] == 0 and financial_data["other_income"] == 0:
            print("No financial data found in text. Using default values if available.")
            
            # Try to use values that might be directly available in the extracted_data
            financial_data["salary_income"] = extracted_data.get("salary_income", 0)
            financial_data["other_income"] = extracted_data.get("other_income", 0)
            financial_data["deductions_80c"] = extracted_data.get("deductions_80c", 0)
            financial_data["home_loan_principal"] = extracted_data.get("home_loan_principal", 0)
            
            # If still no data, set some defaults for testing
            if financial_data["salary_income"] == 0 and financial_data["other_income"] == 0:
                print("WARNING: No financial data found. Using default test values.")
                financial_data["salary_income"] = 800000  # Setting a default for testing
        
        # Run the tax calculation on the financial data
        return self.run_tax_calculation(financial_data)
    
    def calculate_tax_amount(self, net_taxable_income):
        """
        Apply tax slabs according to Indian tax law
        """
        tax = 0
        if net_taxable_income <= 250000:
            tax = 0  # No tax
        elif net_taxable_income <= 500000:
            tax = 0.05 * (net_taxable_income - 250000)  # 5% tax on income above 250,000
        elif net_taxable_income <= 1000000:
            tax = 0.05 * 250000 + 0.2 * (net_taxable_income - 500000)  # 20% tax on income above 500,000
        else:
            tax = 0.05 * 250000 + 0.2 * 500000 + 0.3 * (net_taxable_income - 1000000)  # 30% tax on income above 1,000,000
        
        return tax
    
    def run_tax_calculation(self, financial_data):
        """
        This method calculates the tax for the given financial data.
        Returns the total income, deductions, and calculated tax.
        """
        # Calculate total income
        total_income = financial_data.get("salary_income", 0) + financial_data.get("other_income", 0)
        
        # Calculate total deductions
        # Limit deductions to maximum allowed
        deductions_80c = min(financial_data.get("deductions_80c", 0), 150000)  # Max 1.5L for 80C
        home_loan_principal = min(financial_data.get("home_loan_principal", 0), 200000)  # Example limit
        total_deductions = deductions_80c + home_loan_principal
        
        # Calculate net taxable income
        net_taxable_income = max(0, total_income - total_deductions)
        
        # Calculate base tax amount
        tax = self.calculate_tax_amount(net_taxable_income)
        
        # Apply cess (Health and Education Cess)
        cess = 0.04 * tax  # 4% cess
        total_tax = tax + cess
        
        # Format all values as rounded to 2 decimal places for display
        total_income_rounded = round(total_income, 2)
        total_deductions_rounded = round(total_deductions, 2)
        net_taxable_income_rounded = round(net_taxable_income, 2)
        tax_rounded = round(tax, 2)
        cess_rounded = round(cess, 2)
        total_tax_rounded = round(total_tax, 2)
        
        # Log the calculation for debugging
        print(f"Tax Calculation: Income={total_income_rounded}, Deductions={total_deductions_rounded}, Net={net_taxable_income_rounded}, Tax={tax_rounded}, Cess={cess_rounded}, Total Tax={total_tax_rounded}")
        
        # Return the results as a dictionary
        return {
            "total_income": total_income_rounded,
            "total_deductions": total_deductions_rounded,
            "net_taxable_income": net_taxable_income_rounded,
            "base_tax": tax_rounded,
            "cess": cess_rounded,
            "total_tax": total_tax_rounded,
            "financial_data": financial_data  # Include the extracted financial data
        }

if __name__ == "__main__":
    # Test with sample data
    agent = TaxCalcAgent()
    sample_data = {
        "financial_text": "Salary income: Rs. 1128000, 80C deductions: Rs. 150000"
    }
    result = agent.calculate_tax(sample_data)
    
    # Display results
    print("\nTEST RESULTS:")
    print(f"Total Income: ₹{result['total_income']}")
    print(f"Total Deductions: ₹{result['total_deductions']}")
    print(f"Net Taxable Income: ₹{result['net_taxable_income']}")
    print(f"Base Tax: ₹{result['base_tax']}")
    print(f"Cess (4%): ₹{result['cess']}")
    print(f"Tax Liability: ₹{result['total_tax']}")