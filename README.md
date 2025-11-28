````markdown
# 💰 Automated Bank Statement Analyzer

This project provides a robust, Python-based solution for aggregating, cleaning, and visualizing bank transaction data from multiple `.xls` files. It transforms raw bank statements into actionable insights, showing balance trends, and summarizing monthly debit/credit activity.

---

## ✨ Features

* **Bulk Data Ingestion:** Automatically reads and concatenates multiple bank statement files (`.xls`) from a designated `statements/` directory.
* **Intelligent Data Cleaning:** Handles specific banking statement formats (skips header rows, removes footer/trailing columns, converts string amounts with commas to numeric data types).
* **Time Series Analysis:** Sorts and aggregates data chronologically to provide a continuous financial history.
* **Visual Trend Analysis:** Generates both static (`matplotlib`) and interactive (`plotly`) time-series charts of the account balance over the entire period.
* **Monthly Deep Dive:** Allows for filtering and visualization of balance, debit, and credit activity for specific months.
* **Transaction Filtering:** Includes a custom function to search transaction descriptions and calculate total debit/credit amounts for specific merchants or keywords.

---

## 🛠️ Project Setup

### Prerequisites

You must have Python 3.x installed. The project relies on several key data science libraries:

* **`pandas`:** For data manipulation and cleaning.
* **`matplotlib` & `plotly`:** For data visualization.
* **`num2words`:** For converting numbers to words (used in transaction filtering).

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone [Your Repository URL Here]
    cd [your-project-name]
    ```

2.  **Install Dependencies:**
    ```bash
    pip install pandas matplotlib plotly num2words
    ```

### Data Structure

Place all your bank statement files (e.g., `1763033905327Uc7bP9NWfoP6e7u2.xls`) inside a directory named `statements/` at the root of the project.

````

/bank-analyzer/
├── statements/
│   ├── statement\_jan\_2025.xls
│   └── statement\_feb\_2025.xls
├── BankStatementAnalysis.ipynb  \<-- The main script
└── README.md

````

---

## 🚀 Usage

The entire analysis is performed within the provided Jupyter Notebook or Python script.

### 1. Run the Full Analysis

Execute the cells in the notebook sequentially to:

* Load and clean all data.
* Print the overall date range.
* Generate the full balance time-series chart (`matplotlib` and `plotly` versions).

### 2. Monthly Analysis

Modify the parameters in the **`# Monthly analysis`** section to zoom in on a specific date range:

```python
start_month, end_month = 2, 11
start_year, end_year = 2025, 2025
````

### 3\. Transaction Search

Use the `filter_search` function to analyze spending related to specific keywords.

```python
# Searches for 'hungerbox' in the transaction descriptions
filter_search(selected_data, ['hungerbox', 'Zomato', 'Swiggy'])
```

This function will output the total debited and credited amounts for all matching transactions, and display the filtered DataFrame.

-----

## ⚙️ Customization (Data Cleaning)

The script relies on specific formatting details of the bank statements, particularly:

  * `skiprows=20`: Assumes the data starts on row 21 (skipping 20 rows of headers).
  * `delimiter='\t'`: Assumes the file is tab-separated (`.xls` files saved from online banking often use this).
  * `df = df.iloc[:-1, :]`: Removes the last row (often a "TOTAL" row).
  * `df = df.iloc[:, :-1]`: Removes the last column (often blank or unnecessary).
  * Column Renaming: `df = df.rename(columns={'        Debit': 'Debit'})` is crucial for fixing non-standard characters in the header.

If your bank statements change format, these lines may need adjustment.

-----

## 🤝 Contribution

Feel free to open issues or submit pull requests to improve the script, add support for different bank statement formats, or enhance the visualization features\!

```
```
