import streamlit as st
from resume_data_extractor import extract_text_from_file
from sheet import append_resume_data, phone_exists
from gpt import parse_resume_with_ai

st.set_page_config(page_title="AI Resume Parser", layout="centered")
st.title("AI Resume Parser & Google Sheet Appender")

# File uploader
uploaded_file = st.file_uploader("Upload your resume:", type=["pdf", "docx"])

if uploaded_file:
    with st.spinner("Extracting text from resume..."):
        text = extract_text_from_file(uploaded_file)

    if not text.strip():
        st.error("No readable text found. Please upload a valid PDF or DOCX resume.")
    else:
        st.success("Text extracted successfully.")

        with st.spinner("Parsing resume details using GPT-5-mini..."):
            parsed_data = parse_resume_with_ai(text)

        st.subheader("Review and validate the extracted details below:")

        # Editable fields
        name = st.text_input("Full Name", parsed_data.get("name", ""))
        role = st.text_input("Role / Designation", parsed_data.get("role", ""))
        phone = st.text_input("Phone Number", parsed_data.get("phone", ""))
        email = st.text_input("Email", parsed_data.get("email", ""))
        linkedin = st.text_input("LinkedIn URL", parsed_data.get("linkedin_url", ""))
        address = st.text_area("Address", parsed_data.get("address", ""))
        comment = st.text_area("Comments (optional)", placeholder="Add any notes or remarks here...")

        validated_data = {
            "name": name.strip(),
            "role": role.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "linkedin_url": linkedin.strip(),
            "address": address.strip(),
            "comment": comment.strip()
        }

        st.write("Please confirm all details before appending to Google Sheet.")

        # Check duplicate before submission
        if st.button("Append to Google Sheet"):
            if phone.strip() == "":
                st.error("Please enter a valid phone number before submitting.")
            else:
                with st.spinner("Checking for duplicates..."):
                    try:
                        if phone_exists(phone.strip()):
                            st.warning(f"Phone number {phone.strip()} already exists in the Google Sheet.")
                        else:
                            append_resume_data(validated_data)
                            st.success("Resume details successfully added to Google Sheet!")
                    except Exception as e:
                        st.error(f"Error: {e}")
