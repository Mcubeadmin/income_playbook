#!/usr/bin/env python
# coding: utf-8

# # Importing Data

# In[22]:


# Remove the last row from the DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import glob
import os
import plotly.express as px


# ## Test set

# In[ ]:


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


# In[2]:


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

# In[20]:


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
duplicates = full_df[full_df.duplicated(keep=False)]
sdate, edate = full_df['Txn Date'].iloc[0], full_df['Txn Date'].iloc[-1]
print('Start date of data:', sdate.strftime('%-d %b %Y'))
print('End date of data:', edate.strftime('%-d %b %Y'))
print(f'Duplicate(s) removed: {duplicates.shape[0]}')
# full_df = full_df.drop_duplicates().reset_index(drop=True)
# Display the first few rows
full_df


# In[21]:


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


# In[24]:


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

# In[41]:


month, year = 10, 2025
selected_data = full_df[full_df['Txn Date'].dt.month == month]
selected_data = selected_data[selected_data['Txn Date'].dt.year == year]
fig = px.scatter(
    selected_data,
    x='Txn Date',
    y='Balance',
    hover_data=['Description', 'Debit', 'Credit'],  # Replace 'Description' with your actual column name
    title=f"{selected_data['Txn Date'].dt.strftime('%B %Y').iloc[0]} Transactions",
    labels={'Txn Date': 'Transaction Date', 'Balance': 'Balance'},
    width=1000,
    height=500
)
fig.update_traces(mode='lines+markers', marker=dict(size=5))
fig.update_layout(xaxis_tickangle=90)
fig.show()
selected_data.sort_values(by='Debit', ascending=False).head(10)


# In[42]:


fig = px.scatter(
    selected_data,
    x='Txn Date',
    y='Debit',
    hover_data=['Description'],  # Replace 'Description' with your actual column name
    title=f"{selected_data['Txn Date'].dt.strftime('%B %Y').iloc[0]}",
    labels={'Txn Date': 'Transaction Date', 'Balance': 'Balance'},
    width=1000,
    height=500
)
fig.update_traces(mode='markers', marker=dict(size=5))
fig.update_layout(xaxis_tickangle=90)
fig.show()


# In[58]:


filter_df = full_df[full_df['Description'].str.contains('zerodhabro')]
print(f'Total Amount debited: {filter_df['Debit'].sum()}')
filter_df


# In[ ]:




