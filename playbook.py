#!/usr/bin/env python
# coding: utf-8

# # Importing Data

# In[1]:


# Remove the last row from the DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import glob
import os
import plotly.express as px


# ## Test set

# In[2]:


df = pd.read_csv('statements/1763033905327Uc7bP9NWfoP6e7u2.xls', skiprows=20, delimiter='\t', engine='python')
df.head()
df = df.iloc[:-1, :]
df = df.iloc[:, :-1]
df['Balance'] = pd.to_numeric(df['Balance'].str.replace(',', ''), errors='coerce')
df = df.rename(columns={'        Debit': 'Debit'})
df['Debit'] = pd.to_numeric(df['Debit'].str.replace(',', ''), errors='coerce')
df['Credit'] = pd.to_numeric(df['Credit'].str.replace(',', ''), errors='coerce')
df['Txn Date'] = pd.to_datetime(df['Txn Date'], format='%d %b %Y')
# Display start and end date in '1 Jan 2025' format
sdate, edate = df['Txn Date'].iloc[0], df['Txn Date'].iloc[-1]
print('Start date of data:', sdate.strftime('%-d %b %Y'))
print('End date of data:', edate.strftime('%-d %b %Y'))
df


# In[3]:


plt.figure(figsize=(12, 6))
plt.plot(df['Txn Date'], df['Balance'], '-o')
plt.xlabel('Transaction Date')
plt.ylabel('Balance')
plt.title(f'{sdate.strftime('%-d %b %Y')} to {edate.strftime('%-d %b %Y')}')
plt.xticks(rotation=90)
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.show()


# # Full Data

# In[17]:


all_files = glob.glob(os.path.join('statements', '*.xls'))
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
full_df


# In[5]:


plt.figure(figsize=(15, 6))
plt.plot(full_df['Txn Date'], full_df['Balance'], '-o')
plt.xlabel('Transaction Date')
plt.ylabel('Balance')
plt.title(f'{sdate.strftime('%-d %b %Y')} to {edate.strftime('%-d %b %Y')}')
plt.xticks(rotation=90)
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=40))  # Increase number of x-ticks
plt.tight_layout()
plt.show()


# In[6]:


fig = px.scatter(
    full_df,
    x='Txn Date',
    y='Balance',
    hover_data=['Description', 'Debit', 'Credit'],  # Replace 'Description' with your actual column name
    title=f"{sdate.strftime('%-d %b %Y')} to {edate.strftime('%-d %b %Y')}",
    labels={'Txn Date': 'Transaction Date', 'Balance': 'Balance'},
    width=1000,
    height=500
)
fig.update_traces(mode='lines+markers', marker=dict(size=5))
fig.update_layout(xaxis_tickangle=90)
fig.show()


# # Monthly analysis

# In[120]:


start_month, end_month = 2, 11
start_year, end_year = 2025, 2025

start = start_year * 100 + start_month   # e.g., 2020*100 + 1 = 202001
end   = end_year * 100 + end_month       # e.g., 2022*100 + 6 = 202206

selected_data = full_df[full_df["Value Date"].between(start, end)]

fig = px.scatter(
    selected_data,
    x='Txn Date',
    y='Balance',
    hover_data=['Description', 'Debit', 'Credit'],  # Replace 'Description' with your actual column name
    title=f"Date Range: {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[0]} - {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[-1]}",
    labels={'Txn Date': 'Transaction Date', 'Balance': 'Balance'},
    width=1000,
    height=500
)
fig.update_traces(mode='lines+markers', marker=dict(size=5))
fig.update_layout(xaxis_tickangle=90)
fig.show()

fig = px.scatter(
    selected_data,
    x='Txn Date',
    y='Debit',
    hover_data=['Description'],  # Replace 'Description' with your actual column name
    title=f"Debits: {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[0]} - {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[-1]}",
    labels={'Txn Date': 'Transaction Date', 'Balance': 'Balance'},
    width=1000,
    height=500
)
fig.update_traces(mode='markers', marker=dict(size=5))
fig.update_layout(xaxis_tickangle=90)
fig.show()

fig = px.scatter(
    selected_data,
    x='Txn Date',
    y='Credit',
    hover_data=['Description'],  # Replace 'Description' with your actual column name
    title=f"Credits: {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[0]} - {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[-1]}",
    labels={'Txn Date': 'Transaction Date', 'Balance': 'Balance'},
    width=1000,
    height=500
)
fig.update_traces(mode='markers', marker=dict(size=5))
fig.update_layout(xaxis_tickangle=90)
fig.show()

print(f"Date Range: {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[0]} - {selected_data['Txn Date'].dt.strftime('%B %Y').iloc[-1]}")
print('Top 10 Debits:')
selected_data.sort_values(by='Debit', ascending=False).head(10)


# In[116]:


import num2words

def to_words(amount):
    words = num2words.num2words(amount, lang='en', to='ordinal')
    return words

def filter_search(df, phrases):
    filter_df = df[df['Description'].str.contains('|'.join(phrases))]
    print(f'Search Phrase: {phrases}')
    debit_value, credit_value = filter_df['Debit'].sum(), filter_df['Credit'].sum()
    print(f'Total Amount debited: {debit_value} ({to_words(int(debit_value))}')
    print(f'Total Amount Credited: {credit_value} ({to_words(int(credit_value))})')
    return filter_df


# In[131]:


filter_search(selected_data, ['hungerbox'])

