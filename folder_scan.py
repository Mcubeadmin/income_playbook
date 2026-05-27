import pandas as pd
import glob
import os

def scan_dir():
    all_files = glob.glob(os.path.join('statements', '*.xlsx'))
    dfs = []
    # print(all_files)
    for file in all_files:
        df = pd.read_csv(file, skiprows=20, delimiter='\t', engine='python')
        df = df.iloc[:-1, :]
        df = df.iloc[:, :-1]
        df['Balance'] = pd.to_numeric(df['Balance'].str.replace(',', ''), errors='coerce')
        df = df.rename(columns={'        Debit': 'Debit'})
        df['Debit'] = pd.to_numeric(df['Debit'].str.replace(',', ''), errors='coerce')
        df['Credit'] = pd.to_numeric(df['Credit'].str.replace(',', ''), errors='coerce')
        df['Txn Date'] = pd.to_datetime(df['Txn Date'], format='%d %b %Y')
        dfs.append(df)

    # Concatenate all DataFrames and sort by date
    full_df = pd.concat(dfs, ignore_index=True)
    full_df = full_df.sort_values('Txn Date').reset_index(drop=True)
    full_df["Value Date"] = full_df["Txn Date"].dt.year * 100 + full_df["Txn Date"].dt.month
    duplicates = full_df[full_df.duplicated(keep=False)]
    sdate, edate = full_df['Txn Date'].iloc[0], full_df['Txn Date'].iloc[-1]
    print('Start date of data:', sdate.strftime('%-d %b %Y'))
    print('End date of data:', edate.strftime('%-d %b %Y'))
    print(f'Duplicate(s) removed: {duplicates.shape[0]}')
    # full_df = full_df.drop_duplicates().reset_index(drop=True)
    # Display the first few rows
    return full_df
