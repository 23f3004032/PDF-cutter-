import streamlit as st
import io
import re
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="IITM Paper Cutter Pro", page_icon="✂️")

st.title("✂️ IITM Subject Extractor Pro")
st.write("Bulletproof extraction using keyword boundaries. No OCR or DLLs needed.")

uploaded_file = st.file_uploader("Upload the full term paper PDF", type="pdf")

col1, col2 = st.columns(2)
with col1:
    target_subject = st.text_input("Start Keyword (e.g., MLF)", "").upper().strip()
with col2:
    stop_subject = st.text_input("Stop Keyword (Optional, e.g., MLT, DBMS)", "").upper().strip()

# Master list of IITM subject acronyms to trigger an automatic stop
KNOWN_SUBJECTS = [
    "MLF", "MLT", "MLP", "DBMS", "PDSA", "MAD", "MAD1", "MAD2", "BDM", "SC",
    "MATHS", "STATS", "PYTHON", "ENGLISH", "CT", "TDS", "BA"
]

if uploaded_file and target_subject:
    if st.button("Extract Paper"):
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        writer = PdfWriter()
        
        start_page = -1
        end_page = -1
        total_pages = len(reader.pages)
        
        progress = st.progress(0)
        status = st.empty()
        
        # Determine what words should trigger the cutter to STOP
        if stop_subject:
            stop_triggers = [stop_subject] # Override with your manual input
        else:
            # Auto-stop if it hits any other known IITM subject
            stop_triggers = [s for s in KNOWN_SUBJECTS if s != target_subject]

        for i in range(total_pages):
            progress.progress((i + 1) / total_pages)
            status.text(f"Scanning page {i+1} of {total_pages}...")
            
            # Extract text and uppercase it
            page_text = reader.pages[i].extract_text()
            page_text = page_text.upper() if page_text else ""
            
            # 1. Look for the start page
            if start_page == -1:
                # We use regex word boundaries (\b) so "CT" doesn't trigger on "EXACT"
                pattern_start = r'\b' + re.escape(target_subject) + r'\b'
                if re.search(pattern_start, page_text):
                    start_page = i
                    st.info(f"📍 '{target_subject}' section found starting on Page {i+1}")
            
            # 2. Look for the end page
            else:
                found_stop = False
                for trigger in stop_triggers:
                    pattern_stop = r'\b' + re.escape(trigger) + r'\b'
                    if re.search(pattern_stop, page_text):
                        end_page = i
                        st.info(f"🛑 Next subject indicator '{trigger}' found on Page {i+1}. Stopping.")
                        found_stop = True
                        break
                
                if found_stop:
                    break
        
        # If the target subject was the very last one in the PDF
        if start_page != -1 and end_page == -1:
            end_page = total_pages

        # Finalize and Output
        if start_page != -1:
            for p in range(start_page, end_page):
                writer.add_page(reader.pages[p])
            
            output_stream = io.BytesIO()
            writer.write(output_stream)
            
            st.success(f"✅ Success! Cut {end_page - start_page} pages.")
            st.download_button(
                label="⬇️ Download Extracted PDF",
                data=output_stream.getvalue(),
                file_name=f"{target_subject}_Extracted.pdf",
                mime="application/pdf"
            )
        else:
            st.error(f"❌ Could not find the text '{target_subject}' in this document.")