""" Page for adding projects to the resume.
"""
import streamlit as st
from utils.database import fetch_organisations, add_organisation, fetch_languages
from utils.database import fetch_projectroles_for_org, add_project, upsert_projectrole
from utils.database import fetch_organisation_id
import deepl


# Path to database and templates
db_path = st.session_state.database
deeplapikey = st.session_state.deeplapikey
deepl_client = deepl.DeepLClient(deeplapikey)

# Titel van de app
st.title("Add projects")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")

st.markdown("Use this form to add project details to your resume.")

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id

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


# Add new organisation
st.write("## Add New Organisation")
new_organisation = st.text_input("New organisation:", placeholder="Add the name of a new organisation if you don't find it below.")
department = st.text_input("Department:", placeholder="Add the department.")
submitted_neworg = st.button("Add")

if submitted_neworg:
    add_organisation(db_path, new_organisation, department)

# Fetch list of all organisations
st.write("## Add New Project")
organisations = fetch_organisations(db_path)
organisation_names = [organisation['OrganisationName'] for organisation in organisations]


selected_org = st.selectbox("Select an organisation:", organisation_names,
                            placeholder="Example: Rabobank Nederland, Gemeente Utrecht")
selected_orgid = fetch_organisation_id(db_path, selected_org)

# Get projects
project_and_roles = fetch_projectroles_for_org(db_path, PersonId, selected_org, selected_language_id)
project_names = [project['ProjectName'] for project in project_and_roles]
project_names.append("New project")

selected_projectname = st.selectbox(
    'Select a project:',
    options=project_names
)

if selected_projectname == "New project":
    projectname = st.text_input("Project name", placeholder="Headline title for this project.")
    project_role = st.text_input("Role title", placeholder="Short description of your role, like 'Senior Developer'")
    project_purpose = st.text_area("Purpose", placeholder="Purpose of this role.")
    project_role_text = st.text_area("Your role", placeholder="Describe what your role was in this project.")
    project_proud_of = st.text_area("Proud of", placeholder="Describe you are proud of in this project.")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date", value=None)

else:
    # Show ProjectName for the selected project
    selected_project_id = [project['ProjectId'] for project in project_and_roles if project['ProjectName'] == selected_projectname][0]

    # Get project details for selected project. It should not be a list.
    selected_project = [project for project in project_and_roles if project['ProjectName'] == selected_projectname][0]
    projectname = st.text_input("Project name", selected_project["ProjectName"])
    project_role = st.text_input("Role title", selected_project["ProjectRoleName"])
    project_purpose = st.text_area("Purpose", selected_project["Purpose"])
    project_role_text = st.text_area("Your role", selected_project["ProjectRoleText"])
    project_proud_of = st.text_area("Proud of", selected_project["ProudOf"])
    start_date = st.date_input("Start Date", selected_project["StartDate"])
    end_date = st.date_input("End Date", selected_project["EndDate"])

# Submit-knop
submitted = st.button("Add/Update Project Entry")

# Submit the form
if submitted:
    if selected_org and projectname:
        upsert_projectrole(db_path, PersonId, selected_orgid, projectname, project_role,
                       project_role_text, project_proud_of, start_date, end_date,
                       project_purpose, selected_language_id)
        st.success(f"Project entry for '{projectname}' successfully added/updated!")
    else:
        st.error("Organisation and Project name field is required.")


# Talenlijst
LANGUAGES = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bn': 'Bengali',
    'zh-cn': 'Chinese (Simplified)',
    'nl': 'Nederlands',
    'en-gb': 'English',
    'fr': 'French',
    'de': 'German',
    'hi': 'Hindi',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'es': 'Spanish',
}

# Translation part of the page
st.write("## Translate Project Details")

# Remove source language from the list of destination languages
language_names.remove(selected_language)

dest_language = st.selectbox(
    'Select destination language of your resume:',
    options=language_names
)

# Get the language ID for the selected language. It is just one value, not a list.
source_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == selected_language][0]
dest_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == dest_language][0]

# Get the language code for the selected language
source_lang = [lang for lang in LANGUAGES if LANGUAGES[lang] == selected_language][0]
target_lang = [lang for lang in LANGUAGES if LANGUAGES[lang] == dest_language][0]

# If the length of the source_lang is larger than 2, it is a language code with a region code. Remove the region code.
if len(source_lang) > 2:
    source_lang = source_lang[:2]

print(f"source_lang {source_lang}")
print(f"target_lang {target_lang}")

# Translate the activity with Google Translate
translated_projectname = deepl_client.translate_text(projectname, source_lang=source_lang, target_lang=target_lang)
translated_rolename = deepl_client.translate_text(project_role, source_lang=source_lang, target_lang=target_lang)

if project_purpose:
    translated_purpose = deepl_client.translate_text(project_purpose, source_lang=source_lang, target_lang=target_lang)
else:
    translated_purpose = ""

translated_roletext = deepl_client.translate_text(project_role_text, source_lang=source_lang, target_lang=target_lang)
translated_proudof = deepl_client.translate_text(project_proud_of, source_lang=source_lang, target_lang=target_lang)
edited_projectname = st.text_area("Translated project name:", translated_projectname)
edited_rolename = st.text_area("Translated role name:", translated_rolename)
edited_purpose = st.text_area("Translated purpose:", translated_purpose)
edited_roletext = st.text_area("Translated role description:", translated_roletext)
edited_proudof = st.text_area("Translated proud of:", translated_proudof)

addtransbutton = st.button("Add Translated Project Details")

# Verwerk het formulier
if addtransbutton:
    # add_project(db_path, PersonId, selected_org, edited_projectname, edited_rolename, edited_roletext,
    #                 edited_proudof, start_date, end_date, edited_purpose, dest_language_id)
    upsert_projectrole(db_path, PersonId, selected_orgid, edited_projectname, edited_rolename,
                       edited_roletext, edited_proudof, start_date, end_date,
                       edited_purpose, dest_language_id)
    st.success("Translated project details successfully added!")
