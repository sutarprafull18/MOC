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

# Include custom CSS and logo styling
st.markdown(
    """
    <style>
        body {
            margin: 0;
            padding: 0;
            background: url('background.jpg') no-repeat center center fixed;
            background-size: cover;
            font-family: Arial, sans-serif;
        }
        div[data-testid="stDataFrame"] {
            background-color: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .logo-container {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }
        .logo-container img {
            height: 80px;
            width: auto;
            border-radius: 50%;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
    </style>
    <div class="logo-container">
        <img src="logo.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

def display_excel_data(df):
    """Display Excel data immediately after upload"""
    st.markdown("### 📊 Master File Data")
    st.dataframe(df, use_container_width=True)
    
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
        temp_df = pd.read_excel(master_file)
        pan_column = next((col for col in temp_df.columns if "PAN" in col.upper()), None)
        name_column = next((col for col in temp_df.columns if "NAME" in col.upper()), None)

        if not pan_column or not name_column:
            st.error("❌ Error: Could not find PAN or NAME columns in the master file.")
            return None

        master_df = pd.read_excel(master_file, usecols=[pan_column, name_column])
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            renamed_count = 0
            unmatched_files = []
            processed_files = []
            pan_regex = r"([A-Z]{5}[0-9]{4}[A-Z]{1})"

            progress_bar = st.progress(0)
            status_text = st.empty()

            # First, identify unmatched files
            for uploaded_file in pdf_files:
                match = re.search(pan_regex, uploaded_file.name)
                if not match or (match and match.group(1) not in pan_name_mapping):
                    unmatched_files.append(uploaded_file)

            # Display unmatched files if any
            if unmatched_files:
                st.warning("⚠️ Found files with no matching PAN numbers:")
                for file in unmatched_files:
                    st.text(f"- {file.name}")
                
            # Process all files
            for idx, uploaded_file in enumerate(pdf_files):
                try:
                    match = re.search(pan_regex, uploaded_file.name)
                    if match:
                        pan = match.group(1)
                        status_text.text(f"Processing: {uploaded_file.name}")

                        if pan in pan_name_mapping:
                            # Process matched files
                            original_name = uploaded_file.name
                            remaining_part = original_name[original_name.find(pan) + len(pan):original_name.rfind('.pdf')]
                            name = pan_name_mapping[pan].strip()
                            new_name = f"{pan}{remaining_part} - {name}.pdf"
                            zip_file.writestr(new_name, uploaded_file.getvalue())
                            renamed_count += 1
                            processed_files.append((uploaded_file.name, new_name))
                        else:
                            # Add unmatched files to ZIP with original name
                            zip_file.writestr(f"unmatched/{uploaded_file.name}", uploaded_file.getvalue())
                    else:
                        # Add files without PAN to ZIP with original name
                        zip_file.writestr(f"unmatched/{uploaded_file.name}", uploaded_file.getvalue())

                    progress_bar.progress((idx + 1) / len(pdf_files))

                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")

            # Display results
            if renamed_count > 0:
                st.success(f"✅ Successfully processed {renamed_count} files")
                with st.expander("📋 Processed Files Details", expanded=True):
                    for old_name, new_name in processed_files:
                        st.text(f"✓ {old_name} → {new_name}")

            if unmatched_files:
                with st.expander("⚠️ Unmatched Files (Included in ZIP)", expanded=True):
                    for file in unmatched_files:
                        st.text(f"- {file.name}")

        if renamed_count > 0 or unmatched_files:
            zip_buffer.seek(0)
            return zip_buffer
        return None

    except Exception as e:
        st.error(f"❌ Error processing the files: {e}")
        return None

# Main UI
st.title("📄 PDF Renaming Utility")

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
    - Handles unmatched files
    - Detailed progress tracking
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Step 1: Upload Master File")
    master_file = st.file_uploader("Upload the Master Excel file (XLSX)", type=["xlsx"])
    
    if master_file:
        df = pd.read_excel(master_file)
        display_excel_data(df)

with col2:
    st.markdown("### 📁 Step 2: Upload PDF Files")
    pdf_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

# Floating container for buttons
if master_file or pdf_files:
    st.markdown(
        """
        <div class='floating-container'>
            <iframe srcdoc='
                <button 
                    style="
                        padding: 15px 30px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 25px;
                        cursor: pointer;
                        font-size: 16px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    "
                    onclick="window.parent.document.querySelector(\'button[kind=primary]\').click();">
                    🚀 Process Files
                </button>
            ' width="200" height="60" frameborder="0">
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

# Hidden process button that will be triggered by floating button
if st.button("Process Files", key="hidden_process"):
    if master_file and pdf_files:
        zip_buffer = process_rename(master_file, pdf_files)
        if zip_buffer:
            st.download_button(
                label="📥 Download Renamed Files (ZIP)",
                data=zip_buffer,
                file_name="renamed_files.zip",
                mime="application/zip",
                key="download_button"
            )
    else:
        st.error("⚠️ Please upload both the master file and PDF files.")
