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

[... Previous helper functions remain the same ...]

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
    
    # Initialize session state
    if 'pdf_files' not in st.session_state:
        st.session_state.pdf_files = []

    # File uploader section
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
        
        if uploaded_files:
            st.session_state.pdf_files = uploaded_files
            
            # Show a preview of first few files with scroll
            st.markdown('<div class="files-preview">', unsafe_allow_html=True)
            st.markdown(f'<div class="file-count">Upload Preview ({len(uploaded_files)} files)</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="file-list-scroll">', unsafe_allow_html=True)
                for file in uploaded_files:
                    st.markdown(f'<div class="file-list-item">📄 {file.name}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Clear files button
    if st.session_state.pdf_files:
        if st.button("🗑️ Clear All Files", key="clear_files", type="primary"):
            st.session_state.pdf_files = []
            st.session_state.uploaded_files = None
            st._rerun()  # Force complete rerun to clear the file uploader

    # Process files section
    if st.session_state.pdf_files:
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("🚀 Process Files", key="process_files"):
            if master_file and st.session_state.pdf_files:
                zip_buffer = process_rename(master_file, st.session_state.pdf_files)
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
        st.markdown('</div>', unsafe_allow_html=True)
