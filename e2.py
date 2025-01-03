import os
import pandas as pd
import streamlit as st
from io import BytesIO
from werkzeug.utils import secure_filename
import re

# Function to process the renaming
def process_rename(master_file, folder_path):
    try:
        # Clean the folder path (remove any leading/trailing spaces or quotes)
        folder_path = folder_path.strip().strip('"')

        # Validate the folder path
        if not os.path.exists(folder_path):
            st.error(f"The folder path '{folder_path}' does not exist. Please provide a valid path.")
            return

        if not os.path.isdir(folder_path):
            st.error(f"The provided path '{folder_path}' is not a folder. Please provide a valid folder path.")
            return

        # Read the master Excel file
        temp_df = pd.read_excel(master_file)

        # Display all data in the file
        st.subheader("Data in Master Excel File")
        st.write(temp_df)

        # Display row and column numbers
        rows, cols = temp_df.shape
        st.write(f"Total Rows: {rows}, Total Columns: {cols}")

        # Dynamically find the columns for PAN and NAME
        pan_column = next((col for col in temp_df.columns if "PAN" in col.upper()), None)
        name_column = next((col for col in temp_df.columns if "NAME" in col.upper()), None)

        if not pan_column or not name_column:
            st.error("Error: Could not find PAN or NAME columns in the master file.")
            return

        # Read the necessary columns
        master_df = pd.read_excel(master_file, usecols=[pan_column, name_column])
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        # Debugging: Output the cleaned PAN values
        st.write(f"Cleaned PAN values: {', '.join(pan_name_mapping.keys())}")

        # Get all PDF files in the selected folder
        tds_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

        renamed_count = 0
        error_files = []

        # Regex pattern for matching PAN format (assuming it's always 10 characters like 'AAAAA9999A')
        pan_regex = r"([A-Z]{5}[0-9]{4}[A-Z]{1})"

        for file_name in tds_files:
            try:
                # Extract PAN from file name using regex
                match = re.search(pan_regex, file_name)

                if match:
                    pan = match.group(1)
                    st.write(f"Extracted PAN from filename: {pan}.pdf")

                    # Check if the extracted PAN matches any PAN in the master data
                    if pan in pan_name_mapping:
                        # Generate new filename in the desired format
                        name = pan_name_mapping[pan].strip()
                        new_name = f"{pan} - {name}.pdf"
                        old_file_path = os.path.join(folder_path, file_name)
                        new_file_path = os.path.join(folder_path, new_name)
                        os.rename(old_file_path, new_file_path)
                        renamed_count += 1
                    else:
                        error_files.append(file_name)
                else:
                    error_files.append(file_name)
            except Exception as e:
                error_files.append(f"{file_name} - {str(e)}")

        st.success(f"Total files renamed: {renamed_count}")
        if renamed_count > 0:
            st.write(f"Sample renamed file format: `{pan} - {name}.pdf`")
        if error_files:
            st.warning(f"Some files could not be renamed: {', '.join(error_files)}")

    except Exception as e:
        st.error(f"Error processing the file: {e}")

# Streamlit UI
st.title("PDF Renaming Utility")

# File upload section
uploaded_file = st.file_uploader("Upload the Master Excel file here", type=["xlsx"])

# Show data and row/column numbers as soon as the file is uploaded
if uploaded_file:
    # Read the uploaded Excel file
    temp_df = pd.read_excel(uploaded_file)

    # Display the data
    st.subheader("Data in Master Excel File")
    st.write(temp_df)

    # Display row and column numbers
    rows, cols = temp_df.shape
    st.write(f"Total Rows: {rows}, Total Columns: {cols}")

# Folder selection section
folder_path = st.text_input("Enter the folder path where TDS certificates are stored:")

# Button to trigger the renaming
if st.button("Rename Files"):
    if uploaded_file and folder_path:
        # Process the renaming
        process_rename(uploaded_file, folder_path)
    else:
        st.error("Please upload the master file and provide the folder path.")
