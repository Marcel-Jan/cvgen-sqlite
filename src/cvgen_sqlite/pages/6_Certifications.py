# from pathlib import Path
import streamlit as st
from utils.database import add_certification, fetch_certifications

# Path to database and templates
db_path = st.session_state.database

# Titel van de app
st.title("Certifications Manager")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form to add certifications to your resume.")

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id


# Create forms for editing
certname = st.text_input("Certification Name", placeholder="Example: Microsoft Certified: Azure Fundamentals")
institution = st.text_input("Institution", placeholder="Example: Microsoft")
earningcriteria = st.text_input("Earning Criteria", placeholder="Example: Pass Exam AZ-900: Microsoft Azure Fundamentals")
credentiallink = st.text_input("Credential Link", placeholder="Example: https://www.credly.com/badges/xxxxx-yyyy-zzzzzz232232")
issuedate = st.date_input("Issue Date")
expirydate = st.date_input("Expiry Date", value=None)

# Submit edited results back to database
if st.button("Save Changes"):
    add_certification(db_path, PersonId, certname, institution, issuedate, expirydate, earningcriteria, credentiallink)


# Show certifications
st.write("### Your Certifications")
certifications = fetch_certifications(db_path, PersonId)
# Remove EducationId from the list
for certification in certifications:
    del certification['CertificationId']
    del certification['IssueYear']
st.table(certifications)

