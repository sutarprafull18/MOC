import os
import pandas as pd
import streamlit as st
from io import BytesIO

# Function to process the renaming
def process_rename(master_file, uploaded_pdfs):
    try:
        # Read the master Excel file
        temp_df = pd.read_excel(master_file)

        # Display all data in the file
        st.subheader("Data in Master Excel File")
        st.write(temp_df)

        # Dynamically find the columns for PAN and NAME
        pan_column = next((col for col in temp_df.columns if "PAN" in col.upper()), None)
        name_column = next((col for col in temp_df.columns if "NAME" in col.upper()), None)

        if not pan_column or not name_column:
            st.error("Error: Could not find PAN or NAME columns in the master file.")
            return

        # Read the necessary columns
        master_df = pd.read_excel(master_file, usecols=[pan_column, name_column])
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        renamed_count = 0
        renamed_files = []

        # Process each uploaded PDF
        for pdf_file in uploaded_pdfs:
            try:
                # Extract PAN from the file name
                pan = pdf_file.name.split("_")[0]
                if pan in pan_name_mapping:
                    # Generate new filename in the desired format
                    name = pan_name_mapping[pan].strip()
                    new_name = f"{pan} - {name}.pdf"

                    # Save the renamed file as a downloadable link
                    with open(f"./temp/{new_name}", "wb") as f:
                        f.write(pdf_file.getbuffer())
                    renamed_count += 1
                    renamed_files.append(new_name)  # Add renamed file to the list
                else:
                    renamed_files.append(f"Error: PAN not found for {pdf_file.name}")

            except Exception as e:
                renamed_files.append(f"Error processing {pdf_file.name}: {str(e)}")

        st.success(f"Total files renamed: {renamed_count}")

        # Show renamed files
        if renamed_files:
            st.subheader("Renamed Files:")
            for file in renamed_files:
                st.write(file)

        if renamed_count > 0:
            # Allow users to download renamed files
            for file in renamed_files:
                if "Error" not in file:
                    st.download_button(label=f"Download {file}",
                                       data=open(f"./temp/{file}", "rb"),
                                       file_name=file,
                                       mime="application/pdf")

    except Exception as e:
        st.error(f"Error processing the file: {e}")

# Streamlit UI
st.title("PDF Renaming Utility")

# File upload section for the master Excel file
uploaded_file = st.file_uploader("Upload the Master Excel file here", type=["xlsx"])

# File upload section for PDF files
uploaded_pdfs = st.file_uploader("Upload TDS certificate PDFs here", type=["pdf"], accept_multiple_files=True)

# Show data and row/column numbers as soon as the file is uploaded
if uploaded_file:
    temp_df = pd.read_excel(uploaded_file)
    st.subheader("Data in Master Excel File")
    st.write(temp_df)
    rows, cols = temp_df.shape
    st.write(f"Total Rows: {rows}, Total Columns: {cols}")

# Button to trigger the renaming
if st.button("Rename Files"):
    if uploaded_file and uploaded_pdfs:
        process_rename(uploaded_file, uploaded_pdfs)
    else:
        st.error("Please upload both the master file and the TDS certificate PDFs.")
