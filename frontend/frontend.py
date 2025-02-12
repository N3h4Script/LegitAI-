import streamlit as st
import requests

st.title("Legal Contract Analyzer")

uploaded_file = st.file_uploader("Upload a Contract PDF", type=["pdf"])

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    files = {"file": open("temp.pdf", "rb")}
    response = requests.post("http://127.0.0.1:5000/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        st.subheader("Summary")
        st.write(data["summary"])
        
        st.subheader("Extracted Clauses")
        for clause, label in data["clauses"].items():
            st.write(f"**{label}**: {clause}")
    else:
        st.error("Error processing the contract.")
