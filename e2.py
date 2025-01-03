import os
import pandas as pd
import streamlit as st
from io import BytesIO
from werkzeug.utils import secure_filename

# Function to check if file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'pdf'}

# Function to process and rename PDF files based on PAN from Excel
def rename_files(excel_file, pdf_files):
    # Read the Excel file to extract PAN to Name mapping
    excel_data = pd.read_excel(excel_file)
    
    if 'PAN' not in excel_data.columns or 'NAME' not in excel_data.columns:
        return "PAN or NAME columns are missing in the Excel file."
    
    pan_name_mapping = dict(zip(excel_data['PAN'], excel_data['NAME']))
    
    renamed_files = []
    error_files = []
    
    for pdf_file in pdf_files:
        if allowed_file(pdf_file.name):
            pan = pdf_file.name.split("_")[0]  # Extract PAN assuming the filename starts with PAN
            
            if pan in pan_name_mapping:
                new_filename = f"{pan} - {pan_name_mapping[pan]}.pdf"
                renamed_files.append(new_filename)
            else:
                error_files.append(pdf_file.name)

    if renamed_files:
        success_message = f"Renamed files: {', '.join(renamed_files)}"
    else:
        success_message = "No files were renamed."
        
    if error_files:
        error_message = f"Error: PAN not found for files: {', '.join(error_files)}"
    else:
        error_message = None

    return success_message, error_message


# Streamlit app code
def main():
    st.title("PDF Renaming Utility")
    
    # Upload the Excel file
    excel_file = st.file_uploader("Upload Excel file (PAN - NAME Mapping)", type=["xlsx"])
    
    # Upload multiple PDF files
    pdf_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    
    if excel_file and pdf_files:
        st.write("Processing files...")
        success_message, error_message = rename_files(excel_file, pdf_files)
        
        # Show messages in Streamlit
        if success_message:
            st.success(success_message)
        
        if error_message:
            st.error(error_message)

# Run the app
if __name__ == '__main__':
    main()
