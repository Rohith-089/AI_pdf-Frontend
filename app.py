import streamlit as st
import fitz  # PyMuPDF
import httpx
from transformers import pipeline

API_URL = "https://ai-pdf-backend-nnnt.onrender.com/pdfs"

# Init summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_summary(text: str) -> str:
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

st.title("📄 AI PDF Summarizer")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    filename = uploaded_file.name
    content = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Content")
    st.text_area("PDF Content", content, height=200)

    if st.button("Generate Summary & Submit"):
        with st.spinner("Summarizing..."):
            summary = generate_summary(content)

        st.success("Summary Generated ✅")
        st.text_area("Summary", summary, height=100)

        with st.spinner("Saving to backend..."):
            data = {
                "filename": filename,
                "content": content,
                "summary": summary
            }
            response = httpx.post(API_URL, json=data)
            if response.status_code == 201:
                st.success("Saved to MongoDB!")
            else:
                st.error("Save failed.")

if st.button("Fetch All PDFs"):
    with st.spinner("Fetching..."):
        response = httpx.get(API_URL)
        if response.status_code == 200:
            all_pdfs = response.json()
            for pdf in all_pdfs:
                st.markdown(f"### {pdf['filename']}")
                st.markdown(f"**Summary:** {pdf['summary']}")
        else:
            st.error("Failed to fetch.")
