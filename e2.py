import os
import pandas as pd
import streamlit as st
from io import BytesIO

# Function to process the renaming
def process_rename(master_file, tds_files):
    try:
        # Read the master Excel file
        temp_df = pd.read_excel(master_file)
        st.write("Columns in the uploaded file:", temp_df.columns)

        # Dynamically find the columns for PAN and NAME
        pan_column = next((col for col in temp_df.columns if "PAN" in col.upper()), None)
        name_column = next((col for col in temp_df.columns if "NAME" in col.upper()), None)

        if not pan_column or not name_column:
            st.error("Error: Could not find PAN or NAME columns in the master file.")
            return

        # Read the necessary columns
        master_df = pd.read_excel(master_file, usecols=[pan_column, name_column])
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        renamed_files = []
        error_files = []

        # Process each uploaded PDF file
        for uploaded_file in tds_files:
            try:
                # Read file content as bytes
                file_content = uploaded_file.getvalue()
                file_name = uploaded_file.name

                # Extract PAN from file name
                pan = file_name.split("_")[0]
                if pan in pan_name_mapping:
                    new_name = pan_name_mapping[pan].strip() + ".pdf"
                    renamed_files.append(f"{file_name} -> {new_name}")
                else:
                    error_files.append(file_name)
            except Exception as e:
                error_files.append(f"{file_name} - {str(e)}")

        # Display results
        st.success("Renaming complete!")
        st.write("Renamed Files:")
        st.write(renamed_files)
        if error_files:
            st.warning(f"Some files could not be renamed: {', '.join(error_files)}")

    except Exception as e:
        st.error(f"Error processing the file: {e}")

# Streamlit UI
st.title("PDF Renaming Utility")

# File upload section
uploaded_file = st.file_uploader("Upload the Master Excel file here", type=["xlsx"])

# Upload TDS certificate files
tds_files = st.file_uploader("Upload the TDS certificate files here", type=["pdf"], accept_multiple_files=True)

# Display the data in the master file
if uploaded_file:
    master_df = pd.read_excel(uploaded_file)
    st.write(f"Data in Master Excel File\nTotal Rows: {master_df.shape[0]}, Total Columns: {master_df.shape[1]}")
    st.dataframe(master_df)

# Button to trigger the renaming
if st.button("Rename Files"):
    if uploaded_file and tds_files:
        # Process the renaming
        process_rename(uploaded_file, tds_files)
    else:
        st.error("Please upload both the master file and the TDS certificate files.")
