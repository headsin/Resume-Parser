import streamlit as st
from resume_data_extractor import extract_text_from_file
from sheet import append_resume_data
from gpt import parse_resume_with_ai

st.set_page_config(page_title="AI Resume Parser", layout="centered")
st.title("AI Resume Parser & Google Sheet Appender (Batch Mode)")

# Allow multiple file uploads
uploaded_files = st.file_uploader("Upload your resumes:", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    results = []  # To store parsed results for all resumes

    for idx, uploaded_file in enumerate(uploaded_files):
        st.divider()
        st.subheader(f"Resume {idx + 1}: {uploaded_file.name}")

        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            text = extract_text_from_file(uploaded_file)

        if not text.strip():
            st.error(f"No readable text found in {uploaded_file.name}. Skipping...")
            continue

        with st.spinner(f"Parsing details using GPT-5-mini for {uploaded_file.name}..."):
            parsed_data = parse_resume_with_ai(text)

        st.success(f"Extracted data from {uploaded_file.name}")

        # Create editable fields for this resume
        name = st.text_input(f"Full Name ({uploaded_file.name})", parsed_data.get("name", ""))
        role = st.text_input(f"Role / Designation ({uploaded_file.name})", parsed_data.get("role", ""))
        phone = st.text_input(f"Phone Number ({uploaded_file.name})", parsed_data.get("phone", ""))
        email = st.text_input(f"Email ({uploaded_file.name})", parsed_data.get("email", ""))
        linkedin = st.text_input(f"LinkedIn URL ({uploaded_file.name})", parsed_data.get("linkedin_url", ""))
        address = st.text_area(f"Address ({uploaded_file.name})", parsed_data.get("address", ""))
        comment = st.text_area(f"Comments ({uploaded_file.name})", "")

        # Collect validated info for this resume
        resume_info = {
            "name": name.strip(),
            "role": role.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "linkedin_url": linkedin.strip(),
            "address": address.strip(),
            "comment": comment.strip()
        }
        results.append(resume_info)

    st.divider()
    st.subheader("Summary of all resumes ready to upload:")
    st.write(f"{len(results)} resumes processed")

    # Preview all data
    st.json(results)

    # Append all resumes to Google Sheet
    if st.button("Append All to Google Sheet"):
        success_count = 0
        for data in results:
            try:
                append_resume_data(data)
                success_count += 1
            except Exception as e:
                st.error(f"Error adding {data.get('name', 'Unknown')} to Google Sheet: {e}")
        st.success(f"{success_count}/{len(results)} resumes added successfully!")
