import streamlit as st
import pandas as pd
import re
from io import BytesIO
import base64
import zipfile

def process_rename(master_file, pdf_files):
    try:
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
            return None

        # Read the necessary columns
        master_df = pd.read_excel(master_file, usecols=[pan_column, name_column])
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        # Create a ZIP file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            renamed_count = 0
            error_files = []

            # Regex pattern for matching PAN format
            pan_regex = r"([A-Z]{5}[0-9]{4}[A-Z]{1})"

            for uploaded_file in pdf_files:
                try:
                    # Extract PAN from filename using regex
                    match = re.search(pan_regex, uploaded_file.name)

                    if match:
                        pan = match.group(1)
                        st.write(f"Processing: {uploaded_file.name}")

                        # Check if the extracted PAN matches any PAN in the master data
                        if pan in pan_name_mapping:
                            # Get the original filename parts
                            original_name = uploaded_file.name
                            suffix = original_name[len(pan):]  # Get everything after the PAN
                            
                            # Generate new filename
                            name = pan_name_mapping[pan].strip()
                            new_name = f"{pan}{suffix} - {name}.pdf"
                            
                            # Add file to ZIP
                            zip_file.writestr(new_name, uploaded_file.getvalue())
                            renamed_count += 1
                        else:
                            error_files.append(uploaded_file.name)
                    else:
                        error_files.append(uploaded_file.name)
                except Exception as e:
                    error_files.append(f"{uploaded_file.name} - {str(e)}")

        # Display results
        st.success(f"Total files processed: {renamed_count}")
        if error_files:
            st.warning(f"Files that couldn't be processed: {', '.join(error_files)}")

        # Return the ZIP file if files were processed
        if renamed_count > 0:
            zip_buffer.seek(0)
            return zip_buffer
        return None

    except Exception as e:
        st.error(f"Error processing the files: {e}")
        return None

# Streamlit UI
st.title("PDF Renaming Utility")
st.markdown("""
### Instructions:
1. Upload the Master Excel file containing PAN and NAME columns
2. Upload all PDF files that need to be renamed
3. Click 'Process Files' to rename and download the results
""")

# File upload sections
master_file = st.file_uploader("Upload the Master Excel file (XLSX)", type=["xlsx"])
pdf_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

# Process button
if st.button("Process Files"):
    if master_file and pdf_files:
        zip_buffer = process_rename(master_file, pdf_files)
        if zip_buffer:
            # Create download button for ZIP file
            st.download_button(
                label="Download Renamed Files (ZIP)",
                data=zip_buffer,
                file_name="renamed_files.zip",
                mime="application/zip"
            )
    else:
        st.error("Please upload both the master file and PDF files.")
