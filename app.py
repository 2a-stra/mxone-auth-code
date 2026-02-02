# app.py
'''
Run:
> streamlit run app.py

Source:
https://github.com/2a-stra/mxone-auth-code
'''
import os
from datetime import datetime
import streamlit as st
import csv
import tempfile
from PIL import Image

import zipfile
from pathlib import Path
from io import BytesIO
from zoneinfo import ZoneInfo

from gen_ext_conf3 import read_rows, process_rows, encrypt_config, encr_files

now = datetime.now(ZoneInfo("Asia/Yerevan"))  # current date and time
DT = now.strftime("%Y%m%d")
DATE_TIME = now.strftime("%Y%m%d-%H%M%S")

Path("./%s" % DT).mkdir(parents=True, exist_ok=True)
EXTENSION_FILE = "./%s/extensions-%s.sh" % (DT, DATE_TIME)
AUTH_TXT = "./%s/auth-%s.txt" % (DT, DATE_TIME)


col_1, col_2 = st.columns([8, 1])

with col_1:
    st.image("img/2A-stra_logo.jpg", width=120)

with col_2:
    with st.popover("❓"):
        st.markdown("""
        ### About
        This app:
        - Reads data from csv file with following format:
            MAC,EXTENTION,CSP,Name1,Name2
        - Generate shell script for MX-ONE extensions creation
        - Generates config files for SIP-phones
        - Encrypts config files for deployment
        
        
        **Source:** https://github.com/2a-stra/mxone-auth-code
        """)

st.set_page_config(page_title="Config Generator", layout="wide")
st.title("Config Generator")

uploaded = st.file_uploader("Upload CSV file", type=["csv", "txt"])

if uploaded:

    # --- Read uploaded file for preview ---
    uploaded.seek(0)
    decoded = uploaded.read().decode("utf-8").splitlines()
    reader = csv.reader(decoded)

    preview_rows = list(reader)

    st.subheader("Uploaded File Preview (Raw)")

    if preview_rows:
        # Add line numbers (1-based)
        preview_with_lines = [
            [idx + 1] + row
            for idx, row in enumerate(preview_rows)
        ]

        st.dataframe(
            preview_with_lines,
            width="stretch"
        )
    else:
        st.info("File is empty.")

    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name

    # Parse rows
    rows, warnings, errors = read_rows(tmp_path)

    st.subheader("Imported Rows Preview")

    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.info("No valid rows found.")

    if warnings:
        st.warning("Warnings")
        for w in warnings:
            st.write("•", w)

    if errors:
        st.error("Errors")
        for e in errors:
            st.write("•", e)

    st.divider()

    if errors:
        st.warning("Some rows have errors. Processing anyway.")

    # ------------------- INIT -------------------
    if "generated_files" not in st.session_state:
        st.session_state.generated_files = []
    if "gen_errors" not in st.session_state:
        st.session_state.gen_errors = []
    if "encrypted_files" not in st.session_state:
        st.session_state.encrypted_files = []

    # ------------------- PROCESS BUTTON -------------------
    if st.button("Process", type="primary"):
        if not rows:
            st.warning("No rows to process.")
        else:
            with st.spinner("Processing..."):
                generated_files, gen_errors = process_rows(
                    rows, DT, EXTENSION_FILE, AUTH_TXT
                )

            st.session_state.generated_files = generated_files
            st.session_state.gen_errors = gen_errors

            st.success(f"Generated {len(generated_files)} config files")

    # ------------------- SHOW RESULTS + ACTIONS -------------------
    if st.session_state.generated_files:
        st.write("### Generated Files")

        with st.container(height=300):
            for name in st.session_state.generated_files:
                st.write(name)

        if st.session_state.gen_errors:
            st.error("Errors")
            for e in st.session_state.gen_errors:
                st.write("•", e)

        # Create ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for name in st.session_state.generated_files:
                zipf.write(name, arcname=os.path.basename(name))
        zip_buffer.seek(0)

        col1, col2 = st.columns([3, 1])

        with col1:
            st.download_button(
                "Download All Files (ZIP)",
                zip_buffer,
                file_name=f"generated_files_{DT}.zip",
                mime="application/zip"
            )

        with col2:
            if st.button("🗑️ Clear config files", key="clear_config_files"):
                deleted = []
                errors = []

                for name in st.session_state.generated_files:
                    try:
                        if os.path.exists(name):
                            os.remove(name)
                            deleted.append(name)
                    except Exception as e:
                        errors.append(f"{name}: {e}")

                st.session_state.generated_files = []
                st.session_state.gen_errors = []

                if deleted:
                    st.success(f"Deleted {len(deleted)} files")

                if errors:
                    st.error("Some files could not be deleted:")
                    for e in errors:
                        st.write("•", e)

                st.rerun()

        st.divider()

        # ------------------- ENCRYPT BUTTON -------------------
        if st.button("🔐 Encrypt", type="secondary"):
            if not rows:
                st.warning("No rows available to encrypt.")
            else:
                with st.spinner("Encrypting configuration files..."):
                    try:
                        outputs, encr_errors = encrypt_config(rows, DT)
                        st.success("Encryption completed successfully.")
                    except Exception as e:
                        st.error(f"Encryption failed: {e}")

                    if outputs:
                        st.write("### Encryption Output")
                        with st.container(height=300):
                            for out in outputs:
                                if out:
                                    st.text(out)

                    if encr_errors:
                        st.error("Errors")
                        for e in encr_errors:
                            st.write("•", e)

            st.session_state.encrypted_files = encr_files(st.session_state.generated_files, "%s/"%DT)

    if st.session_state.encrypted_files:

        # Create ZIP
        zip_buffer2 = BytesIO()
        with zipfile.ZipFile(zip_buffer2, "w", zipfile.ZIP_DEFLATED) as zipf2:
            for name in st.session_state.encrypted_files:
                zipf2.write(name, arcname=os.path.basename(name))
        zip_buffer2.seek(0)

        col3, col4 = st.columns([3, 1])

        with col3:
            st.download_button(
            "Download Encrypted Files (ZIP)",
            zip_buffer2,
            file_name=f"encrypted_files_{DT}.zip",
            mime="application/zip"
        )

        with col4:
            if st.button("🗑️ Clear encrypted files", key="clear_encr_files"):
                deleted = []
                errors = []

                for name in st.session_state.encrypted_files:
                    try:
                        if os.path.exists(name):
                            os.remove(name)
                            deleted.append(name)
                    except Exception as e:
                        errors.append(f"{name}: {e}")

                st.session_state.encrypted_files = []

                if deleted:
                    st.success(f"Deleted {len(deleted)} files")

                if errors:
                    st.error("Some files could not be deleted:")
                    for e in errors:
                        st.write("•", e)

                st.rerun()