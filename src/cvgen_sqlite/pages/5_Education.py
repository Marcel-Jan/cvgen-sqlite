# from pathlib import Path
import streamlit as st
from utils.database import add_education, fetch_languages, fetch_educations
from utils.database import upsert_education, fetch_education


# Path to database and templates
db_path = st.session_state.database

# Titel van de app
st.title("Education Manager")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form to add education details to your resume.")

# Fetch list of all languages
languages = fetch_languages(db_path)
language_names = [language['LanguageName'] for language in languages]

# Streamlit multiselect for project selection
selected_language = st.selectbox(
    'Select the language of your resume:',
    options=language_names
)

# Get the language ID for the selected language. It is just one value, not a list.
selected_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == selected_language][0]

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id


# Fetch education details
st.write("## Add Education")
educations = fetch_educations(db_path, PersonId, selected_language_id)
education_names = [education['Institution'] + " - " + education['FieldOfStudy'] for education in educations]

# Add option for new organisation
education_names.append("New education")

selected_eduname = st.selectbox(
    'Select an education institution and field of study:',
    options=education_names
)

if selected_eduname == "New education":
    degree = st.text_input("Degree", placeholder="Example: Bachelor of Science in Computer Science")
    institution = st.text_input("Institution", placeholder="Example: Universiteit Utrecht")
    fieldofstudy = st.text_input("Field Of Study", placeholder="Example: Chemical Engineering")
    graduation_date = st.date_input("Graduation Date")
    activities = st.text_input("Activities")
    description = st.text_area("Description", placeholder="Describe your education.")

else:
    # Get education id for the selected education
    education_id = [education['EducationId'] for education in educations if education['Institution'] + " - " + education['FieldOfStudy'] == selected_eduname][0]

    # Get details for selected education
    education = fetch_education(db_path, education_id)

    degree = st.text_input("Degree", education['Degree'])
    institution = st.text_input("Institution", education['Institution'])
    fieldofstudy = st.text_input("Field Of Study", education['FieldOfStudy'])
    graduation_date = st.date_input("Graduation Date", education['GraduationDate'])
    activities = st.text_input("Activities", education['Activities'])
    description = st.text_area("Description", education['Description'])


# Submit-knop
submitted = st.button("Add/update Education")

# Verwerk het formulier
if submitted:
    if institution:
        upsert_education(db_path, PersonId, degree, institution, fieldofstudy, 
                      graduation_date, description, activities, selected_language_id)
        st.success(f"Education entry for '{institution}' successfully added/updated!")
    else:
        st.error("Institution field is required.")

# Show Educations
st.write("### Your list of education details:")
educations = fetch_educations(db_path, PersonId, selected_language_id)

# Remove EducationId from the list
for education in educations:
    del education['EducationId']
    del education['Activities']
    del education['GraduationYear']
st.table(educations)
