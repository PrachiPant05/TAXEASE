# Tax calculation test script
from tax_agents.tax_calc_agent import TaxCalcAgent

def test_tax_calculation():
    # Create an instance of the TaxCalcAgent without the LLM client
    tax_calc = TaxCalcAgent()
    
    # Test case 1: Income below 2.5L (no tax)
    test_data_1 = {
        "salary_income": 200000,
        "other_income": 0,
        "deductions_80c": 0,
        "home_loan_principal": 0
    }
    result_1 = tax_calc.run_tax_calculation(test_data_1)
    print("Test Case 1 (Income below 2.5L):")
    print(f"Total Income: ₹{result_1['total_income']}")
    print(f"Net Taxable Income: ₹{result_1['net_taxable_income']}")
    print(f"Tax Liability: ₹{result_1['total_tax']}")
    print("-" * 50)
    
    # Test case 2: Income between 2.5L and 5L (5% tax slab)
    test_data_2 = {
        "salary_income": 400000,
        "other_income": 25000,
        "deductions_80c": 50000,
        "home_loan_principal": 0
    }
    result_2 = tax_calc.run_tax_calculation(test_data_2)
    print("Test Case 2 (Income between 2.5L and 5L):")
    print(f"Total Income: ₹{result_2['total_income']}")
    print(f"Net Taxable Income: ₹{result_2['net_taxable_income']}")
    print(f"Tax Liability: ₹{result_2['total_tax']}")
    print("-" * 50)
    
    # Test case 3: Income between 5L and 10L (20% tax slab)
    test_data_3 = {
        "salary_income": 700000,
        "other_income": 50000,
        "deductions_80c": 150000,
        "home_loan_principal": 50000
    }
    result_3 = tax_calc.run_tax_calculation(test_data_3)
    print("Test Case 3 (Income between 5L and 10L):")
    print(f"Total Income: ₹{result_3['total_income']}")
    print(f"Net Taxable Income: ₹{result_3['net_taxable_income']}")
    print(f"Tax Liability: ₹{result_3['total_tax']}")
    print("-" * 50)
    
    # Test case 4: Income above 10L (30% tax slab)
    test_data_4 = {
        "salary_income": 1128000,  # This matches your original value
        "other_income": 0,
        "deductions_80c": 150000,
        "home_loan_principal": 0
    }
    result_4 = tax_calc.run_tax_calculation(test_data_4)
    print("Test Case 4 (Income above 10L):")
    print(f"Total Income: ₹{result_4['total_income']}")
    print(f"Net Taxable Income: ₹{result_4['net_taxable_income']}")
    print(f"Tax Liability: ₹{result_4['total_tax']}")
    print("-" * 50)

if __name__ == "__main__":
    test_tax_calculation()