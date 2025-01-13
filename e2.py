import streamlit as st
import pandas as pd
import re
from io import BytesIO
import base64
import zipfile
import requests
import math
import time

def get_image_from_url(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except Exception as e:
        st.error(f"Error loading image from {url}: {str(e)}")
        return None

st.set_page_config(page_title="PDF Renaming Utility", page_icon="📄", layout="wide")

BACKGROUND_URL = "https://raw.githubusercontent.com/sutarprafull18/MOC/refs/heads/main/background.jpg"
LOGO_URL = "https://raw.githubusercontent.com/sutarprafull18/MOC/refs/heads/main/logo.png"

background_image = get_image_from_url(BACKGROUND_URL)
if background_image:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{background_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center center;
        }}
        .scrollable-container {{
            max-height: 300px;
            overflow-y: auto;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
        }}
        .file-list-scroll {{
            max-height: 150px;
            overflow-y: auto;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            scrollbar-width: thin;
            scrollbar-color: #4CAF50 #f0f0f0;
        }}
        .file-list-scroll::-webkit-scrollbar {{
            width: 8px;
        }}
        .file-list-scroll::-webkit-scrollbar-track {{
            background: #f0f0f0;
            border-radius: 4px;
        }}
        .file-list-scroll::-webkit-scrollbar-thumb {{
            background-color: #4CAF50;
            border-radius: 4px;
        }}
        .file-item {{
            padding: 8px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .clear-button {{
            background-color: #dc3545 !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 4px !important;
            cursor: pointer !important;
            width: 100% !important;
        }}
        .clear-button:hover {{
            background-color: #c82333 !important;
        }}
        .button-container {{
            position: sticky;
            bottom: 20px;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 100;
        }}
        .file-count {{
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 10px;
            padding: 5px;
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 5px;
            display: inline-block;
        }}
        .file-list-item {{
            padding: 5px;
            margin: 2px 0;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .upload-section {{
            margin-bottom: 20px;
        }}
        .files-preview {{
            margin-top: 10px;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
        }}
        .floating-clear-container {{
            position: fixed;
            right: 20px;
            bottom: 20px;
            z-index: 1000;
        }}
        .floating-clear-button {{
            background-color: #dc3545 !important;
            color: white !important;
            padding: 10px 20px !important;
            border-radius: 5px !important;
            border: none !important;
            cursor: pointer !important;
            font-size: 1em !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        .floating-clear-button:hover {{
            background-color: #c82333 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

logo_image = get_image_from_url(LOGO_URL)
if logo_image:
    st.markdown(
        f"""
        <style>
            .logo-container {{
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1000;
            }}
            .logo-container img {{
                height: 80px;
                width: auto;
                border-radius: 50%;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
            div[data-testid="stDataFrame"] {{
                background-color: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .stButton > button {{
                width: 100%;
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                margin-top: 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
            .stButton > button:hover {{
                background-color: #45a049;
            }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_image}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True
    )

def display_files_in_container(files, container_title):
    """Display files in a scrollable container"""
    if files:
        files_html = "".join([f'<div class="file-item">{file}</div>' for file in files])
        st.markdown(
            f"""
            <div class="scrollable-container">
                {files_html}
            </div>
            """,
            unsafe_allow_html=True
        )

def display_excel_data(df):
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
        master_df[pan_column] = master_df[pan_column].str.upper()
        pan_name_mapping = dict(zip(master_df[pan_column], master_df[name_column]))

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            renamed_count = 0
            unmatched_files = []
            processed_files = []
            pan_regex = r"([A-Za-z]{5}[0-9]{4}[A-Za-z]{1})"

            progress_bar = st.progress(0)
            status_text = st.empty()

            for uploaded_file in pdf_files:
                match = re.search(pan_regex, uploaded_file.name)
                if not match or (match and match.group(1).upper() not in pan_name_mapping):
                    unmatched_files.append(uploaded_file.name)

            if unmatched_files:
                st.warning(f"⚠️ Found {len(unmatched_files)} files with no matching PAN numbers:")
                display_files_in_container(unmatched_files, "Unmatched Files")

            for idx, uploaded_file in enumerate(pdf_files):
                try:
                    match = re.search(pan_regex, uploaded_file.name)
                    if match:
                        pan = match.group(1).upper()
                        status_text.text(f"Processing: {uploaded_file.name}")

                        if pan in pan_name_mapping:
                            original_name = uploaded_file.name
                            remaining_part = original_name[original_name.lower().find(pan.lower()) + len(pan):original_name.rfind('.pdf')]
                            name = pan_name_mapping[pan].strip()
                            new_name = f"{pan}{remaining_part} - {name}.pdf"
                            zip_file.writestr(new_name, uploaded_file.getvalue())
                            renamed_count += 1
                            processed_files.append(f"✓ {original_name} → {new_name}")
                        else:
                            zip_file.writestr(f"unmatched/{uploaded_file.name}", uploaded_file.getvalue())
                    else:
                        zip_file.writestr(f"unmatched/{uploaded_file.name}", uploaded_file.getvalue())

                    progress_bar.progress((idx + 1) / len(pdf_files))

                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")

            if renamed_count > 0:
                st.success(f"✅ Successfully processed {renamed_count} files")
                with st.expander("📋 Processed Files Details", expanded=True):
                    display_files_in_container(processed_files, "Processed Files")

        if renamed_count > 0 or unmatched_files:
            zip_buffer.seek(0)
            return zip_buffer
        return None

    except Exception as e:
        st.error(f"❌ Error processing the files: {e}")
        return None

# Initialize session states
if 'pdf_files' not in st.session_state:
    st.session_state.pdf_files = []
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0

st.title("📄 PDF Renaming Utility")

header_col1, header_col2 = st.columns(2)

with header_col1:
    st.markdown("""
    ### 📌 Instructions:
    1. Upload the Master Excel file containing PAN and NAME columns
    2. Upload PDF files that need to be renamed
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
    
    def clear_files():
        st.session_state.pdf_files = []
        st.session_state.file_uploader_key += 1
    
    # File uploader section with key from session state
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"file_uploader_{st.session_state.file_uploader_key}"
        )
        
        if uploaded_files:
            st.session_state.pdf_files = uploaded_files
            
            # Show a preview of files with scroll
            st.markdown('<div class="files-preview">', unsafe_allow_html=True)
            st.markdown(f'<div class="file-count">Upload Preview ({len(uploaded_files)} files)</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="file-list-scroll">', unsafe_allow_html=True)
                for file in uploaded_files:
                    st.markdown(f'<div class="file-list-item">📄 {file.name}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Clear files button (in original position) and floating button
    if st.session_state.pdf_files:
        # Original clear button (hidden but functional)
        if st.button("🗑️ Clear All Files", key="clear_files", type="primary"):
            clear_files()
            st.rerun()
            
        # Floating clear button
        st.markdown("""
            <div class="floating-clear-container">
                <button class="floating-clear-button" onclick="document.querySelector('button[data-testid=\\"clear_files\\"]').click()">
                    🗑️ Clear All Files
                </button>
            </div>
        """, unsafe_allow_html=True)

    # Process files section
    if st.session_state.pdf_files:
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("🚀 Process Files", key="process_files"):
            if master_file and st.session_state.pdf_files:
                zip_buffer = process
