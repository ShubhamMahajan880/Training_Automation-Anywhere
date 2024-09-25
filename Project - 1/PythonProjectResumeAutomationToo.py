import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import re

# Function to read PDF files
def read_pdf(file):
    reader = PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'
    return text

# Function to read Word files
def read_docx(file):
    doc = Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Function to calculate ATS score
def calculate_ats_score(resume_text, job_description):
    resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))
    job_keywords = set(re.findall(r'\b\w+\b', job_description.lower()))
    matched_keywords = resume_keywords.intersection(job_keywords)
    
    score = len(matched_keywords)
    return score, matched_keywords

# Main function to run the Streamlit app
def main():
    st.title("ATS Score Checker")
    st.write("Upload your resume and input a job description to check ATS compatibility.")

    uploaded_file = st.file_uploader("Choose a PDF or Word document", type=['pdf', 'docx'])
    job_description = st.text_area("Job Description", height=150)

    if uploaded_file is not None and job_description:
        # Read the content of the uploaded file
        if uploaded_file.type == "application/pdf":
            resume_text = read_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = read_docx(uploaded_file)

        st.subheader("Resume Content")
        st.write(resume_text)

        # Calculate ATS score
        score, matched_keywords = calculate_ats_score(resume_text, job_description)
        st.subheader("ATS Score")
        st.write(f"Your ATS score is: {score} (based on matched keywords)")

        # Suggestions for improvement
        st.write("### Suggestions for Improvement:")
        if matched_keywords:
            st.write(f"- You matched the following keywords: {', '.join(matched_keywords)}")
        else:
            st.write("- No keywords matched. Consider adding relevant keywords from the job description.")

    if st.button("Download Report"):
        # Implement report download functionality (not shown here)
        st.write("Feature coming soon!")

if __name__ == "__main__":
    main()
