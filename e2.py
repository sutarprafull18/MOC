import streamlit as st
import pandas as pd
import re
from io import BytesIO
import base64
import zipfile

# Set page configuration
st.set_page_config(
    page_title="PDF Renaming Utility",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .data-stats {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def display_excel_data(df):
    """Display Excel data immediately after upload"""
    st.markdown("### 📊 Master File Data")
    st.dataframe(df, use_container_width=True)
    
    # Calculate and display data statistics
    rows = len(df)
    total_data_points = rows + (rows - 1)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", rows)
    with col2:
        st.metric("Total Data Points", total_data_points)
    with col3:
        st.metric("Total Columns", len(df.columns))

def process_rename(master_file, pdf_files):
    try:
        # Read the master Excel file
        temp_df = pd.read_excel(master_file)

        # Dynamically find the columns for PAN and NAME
        pan_column = next((col for col in temp_df.columns if "PAN" in col.upper()), None)
        name_column = next((col for col in temp_df.columns if "NAME" in col.upper()), None)

        if not pan_column or not name_column:
            st.error("❌ Error: Could not find PAN or NAME columns in the master file.")
            return None

        # Read the necessary columns
        master_df = pd.read_excel(master_file, usecols=[pan_column, name_column])
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        # Create a ZIP file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            renamed_count = 0
            error_files = []
            processed_files = []

            # Regex pattern for matching PAN format
            pan_regex = r"([A-Z]{5}[0-9]{4}[A-Z]{1})"

            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, uploaded_file in enumerate(pdf_files):
                try:
                    # Extract PAN from filename using regex
                    match = re.search(pan_regex, uploaded_file.name)

                    if match:
                        pan = match.group(1)
                        status_text.text(f"Processing: {uploaded_file.name}")

                        # Check if the extracted PAN matches any PAN in the master data
                        if pan in pan_name_mapping:
                            # Preserve the original filename structure
                            original_name = uploaded_file.name
                            # Extract the part after PAN (e.g., _Q1_2025-26)
                            remaining_part = original_name[original_name.find(pan) + len(pan):original_name.rfind('.pdf')]
                            
                            # Generate new filename
                            name = pan_name_mapping[pan].strip()
                            new_name = f"{pan}{remaining_part} - {name}.pdf"
                            
                            # Add file to ZIP
                            zip_file.writestr(new_name, uploaded_file.getvalue())
                            renamed_count += 1
                            processed_files.append((uploaded_file.name, new_name))
                        else:
                            error_files.append(uploaded_file.name)
                    else:
                        error_files.append(uploaded_file.name)

                    # Update progress bar
                    progress_bar.progress((idx + 1) / len(pdf_files))

                except Exception as e:
                    error_files.append(f"{uploaded_file.name} - {str(e)}")

        # Display results in a formatted way
        if renamed_count > 0:
            st.success(f"✅ Successfully processed {renamed_count} files")
            
            # Display processed files
            with st.expander("📋 Processed Files Details", expanded=True):
                for old_name, new_name in processed_files:
                    st.text(f"✓ {old_name} → {new_name}")

        if error_files:
            with st.expander("⚠️ Files with Errors", expanded=True):
                for error_file in error_files:
                    st.warning(f"⚠️ {error_file}")

        # Return the ZIP file if files were processed
        if renamed_count > 0:
            zip_buffer.seek(0)
            return zip_buffer
        return None

    except Exception as e:
        st.error(f"❌ Error processing the files: {e}")
        return None

# Main UI
st.title("📄 PDF Renaming Utility")

# Create two columns for the header
header_col1, header_col2 = st.columns(2)

with header_col1:
    st.markdown("""
    ### 📌 Instructions:
    1. Upload the Master Excel file containing PAN and NAME columns
    2. Upload all PDF files that need to be renamed
    3. Click 'Process Files' to rename and download the results
    """)

with header_col2:
    st.markdown("""
    ### 🎯 Features:
    - Preserves original file structure
    - Batch processing
    - Secure file handling
    - Detailed progress tracking
    """)

# File upload sections with better styling
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Step 1: Upload Master File")
    master_file = st.file_uploader("Upload the Master Excel file (XLSX)", type=["xlsx"])
    
    # Display Excel data immediately after upload
    if master_file:
        df = pd.read_excel(master_file)
        display_excel_data(df)

with col2:
    st.markdown("### 📁 Step 2: Upload PDF Files")
    pdf_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

# Process button
if st.button("🚀 Process Files"):
    if master_file and pdf_files:
        zip_buffer = process_rename(master_file, pdf_files)
        if zip_buffer:
            # Create download button for ZIP file
            st.download_button(
                label="📥 Download Renamed Files (ZIP)",
                data=zip_buffer,
                file_name="renamed_files.zip",
                mime="application/zip",
                key="download_button"
            )
    else:
        st.error("⚠️ Please upload both the master file and PDF files.")
