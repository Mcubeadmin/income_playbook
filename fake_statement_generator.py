import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def create_fake_statement(filename="fake_statement_demo.xlsx", num_rows=150):
    # 1. Generate realistic synthetic financial data
    start_date = datetime(2025, 1, 1)
    
    dates = [start_date + timedelta(days=i, hours=random.randint(0, 23)) for i in range(num_rows)]
    dates.sort()
    
    # Random realistic transaction narration strings
    sample_details = [
        "WDL TFR UPI/DR/SWIGGY/2026",
        "WDL TFR UPI/DR/ZOMATO/9932",
        "NET BANKING / NEFT / IIT-CAMPUS-FEES",
        "WDL TFR UPI/DR/ZERODHA/STOCK",
        "NFX/RAJA/MONTHLY-SUB",
        "CREDIT / INTEREST REWARD / BANK",
        "SALARY / MONTHLY / TECH-CORP",
        "WDL TFR UPI/DR/AMAZON/ORDER",
        "ATM CASH WITHDRAWAL",
        "NEFT RECEIVED / FROM-PARENT-ACC"
    ]
    
    details = [random.choice(sample_details) for _ in range(num_rows)]
    
    debits = []
    credits = []
    
    for desc in details:
        if "SALARY" in desc:
            credits.append(random.randint(80000, 150000))
            debits.append(0)
        elif "RECEIVED" in desc or "INTEREST" in desc:
            credits.append(random.randint(500, 10000))
            debits.append(0)
        elif "IIT" in desc or "ZERODHA" in desc:
            debits.append(random.randint(10000, 40000))
            credits.append(0)
        else:
            debits.append(random.randint(50, 3000))
            credits.append(0)
            
    # Calculate a running balance matching the transactions sequentially
    starting_balance = 50000.00
    balances = []
    current_balance = starting_balance
    
    for d, c in zip(debits, credits):
        current_balance = current_balance - d + c
        balances.append(current_balance)
        
    # Build core dataframe matching your exact column names
    df_core = pd.DataFrame({
        "Date": [d.strftime("%d/%m/%Y") for d in dates],
        "Details": details,
        "Debit": debits,
        "Credit": credits,
        "Balance": balances
    })
    
    # 2. Add the Bank Header Simulation (Skiprows=17 matching)
    # This pads the top of the Excel sheet so your dashboard skips it cleanly
    header_padding = [["--- SIMULATED BANK PRIVATE STATEMENT NETWORK ---"]]
    for i in range(16):
        header_padding.append([f"Bank Metadata Property Code Label Line {i+1}"])
        
    df_header = pd.DataFrame(header_padding)
    
    # 3. Add the Bank Footer Simulation (Skipfooter=8 matching)
    footer_padding = []
    for i in range(8):
        footer_padding.append([f"Footer Legal Disclaimer Line Note {i+1}", "", "", "", ""])
    df_footer = pd.DataFrame(footer_padding, columns=["Date", "Details", "Debit", "Credit", "Balance"])
    
    # Write everything cleanly to an Excel file using openpyxl engine
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        # Write top padding junk
        df_header.to_excel(writer, sheet_name="Sheet1", startrow=0, startcol=0, header=False, index=False)
        # Write actual payload starting precisely at row 17 (0-indexed index 17)
        df_core.to_excel(writer, sheet_name="Sheet1", startrow=17, startcol=0, index=False)
        # Write trailing bottom footer records immediately following core payload rows
        df_footer.to_excel(writer, sheet_name="Sheet1", startrow=17 + len(df_core) + 1, startcol=0, index=False)

    print(f"✨ Successfully generated pristine mock data sheet: '{filename}'")

if __name__ == "__main__":
    create_fake_statement()