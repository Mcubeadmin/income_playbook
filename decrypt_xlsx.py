import io
import os
from pathlib import Path
import msoffcrypto
import pandas as pd


def decrypt_xlsx_to_xls(folder_path, password):
    # Convert string path to a Path object
    directory = Path(folder_path)

    if not directory.exists():
        print(f"Error: The directory '{folder_path}' does not exist.")
        return

    print(f"Scanning folder: {directory.resolve()}\n" + "-" * 40)

    # Find all .xlsx files in the folder
    xlsx_files = list(directory.glob("*.xlsx"))

    if not xlsx_files:
        print("No .xlsx files found in this folder.")
        return

    for file_path in xlsx_files:
        print(f"Processing: {file_path.name}...")

        try:
            # 1. Open and decrypt the file into memory
            with open(file_path, "rb") as f:
                office_file = msoffcrypto.OfficeFile(f)

                # Check if the file actually requires a password
                if office_file.is_encrypted():
                    decrypted_stream = io.BytesIO()
                    office_file.load_key(password=password)
                    office_file.decrypt(decrypted_stream)
                    decrypted_stream.seek(0)
                    print(f"  -> Successfully decrypted in memory.")
                else:
                    # If it's not encrypted, read directly from the original file path
                    decrypted_stream = file_path
                    print(f"  -> File was not encrypted. Reading directly.")

            # 2. Load into Pandas
            # We read all sheets to make sure nothing is left behind
            excel_file = pd.ExcelFile(decrypted_stream)

            # 3. Create the new .xls file path
            # Change step 3 and 4 in your loop to this:

            # 3. Create the new .xlsx file path (Changed from .xls)
            xls_file_path = file_path.with_name(f"decrypted_{file_path.name}")

            # 4. Write back out using the standard modern openpyxl engine
            with pd.ExcelWriter(xls_file_path, engine="openpyxl") as writer:
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"  🎉 Saved clean copy as: {xls_file_path.name}\n")

        except Exception as e:
            print(f"  ❌ Failed to process {file_path.name}. Error: {e}\n")


# --- CONFIGURATION ---
# Use '.' for the current folder where the script runs, or provide an absolute path
TARGET_FOLDER = "./statements"
FILE_PASSWORD = "MOHAM13012001"

# Run the automation
decrypt_xlsx_to_xls(TARGET_FOLDER, FILE_PASSWORD)