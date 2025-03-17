""" Work Experience page
"""
import streamlit as st
from utils.database import add_organisation, fetch_languages, fetch_experience_for_org
from utils.database import fetch_organisations, fetch_organisation_id, upsert_experience
import deepl


# Path to database and templates
db_path = st.session_state.database
deeplapikey = st.session_state.deeplapikey
deepl_client = deepl.DeepLClient(deeplapikey)

# Titel van de app
st.title("Resume - Work Experience")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form to add or change work experience on your resume.")


# Fetch list of all languages
languages = fetch_languages(db_path)
language_names = [language['LanguageName'] for language in languages]

# Streamlit multiselect for work experience selection
selected_language = st.selectbox(
    'Select the language of your resume:',
    options=language_names
)

# Get the language ID for the selected language. It is just one value, not a list.
selected_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == selected_language][0]

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id

# Get organisation
organisations = fetch_organisations(db_path)
# st.write(activities)

# Dropdown menu for selecting the activity
org_names = [organisation['OrganisationName'] for organisation in organisations]
# Add option for new organisation
org_names.append("New organisation")

selected_orgname = st.selectbox(
    'Select an organisation:',
    options=org_names
)

if selected_orgname == "New organisation":
    org_name = st.text_input("Organisation name", "")
    org_dept = st.text_input("Departement", "")

    submitted = st.button("Add New Organisation")

    if submitted:
        add_organisation(db_path, org_name, org_dept)
        st.success("Organisation successfully added!")
    
    selected_org_id = fetch_organisation_id(db_path, org_name)

else:
    # Show OrganisationName for the selected organisation
    selected_org_id = fetch_organisation_id(db_path, selected_orgname)

st.write("## Work Experience")

if selected_org_id is None:
    # If you choose "New Organisation" there is no OrganisationId yet
    # and so the rest of the page does not work yet.
    st.warning("You need to select or create an organisation first.")
    st.stop()

else:
    # Fetch introduction text
    experiences = fetch_experience_for_org(db_path, PersonId, selected_org_id, selected_language_id)
    exp_names = [experience['ShortDescription'] for experience in experiences]
    exp_names.append("New work experience")

    selected_exp = st.selectbox("Select a work experience:", exp_names)

    text_area_height = 500

    if selected_exp == "New work experience":
        # If you don't add a form you will find going from the first field
        # to the next will reload the page and you lose the data you entered.
        with st.form("new_experience_form"):
            exp_jobtitle = st.text_input("Job Title:")
            exp_shortdesc = st.text_input("Description in one sentence:")
            exp_description = st.text_area("Full description:", "", text_area_height)
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date", value=None)

            submitted = st.form_submit_button("Add New Work Experience")

            if submitted:
                upsert_experience(db_path, PersonId, selected_org_id, exp_jobtitle, exp_shortdesc,
                                exp_description, start_date, end_date, selected_language_id)
                st.success("Work Experience successfully added/updated!")

    else:
        # Show Experience for the selected experience
        selected_exp_id = [experience['ExperienceId'] for experience in experiences if experience['ShortDescription'] == selected_exp][0]

        # Get experience details for selected experience. It should not be a list.
        selected_experience = [experience for experience in experiences if experience['ShortDescription'] == selected_exp][0]
        exp_jobtitle = st.text_input("Job Title:", selected_experience['JobTitle'])
        exp_shortdesc = st.text_input("Description in one sentence:", selected_experience['ShortDescription'])
        exp_description = st.text_area("Full description:", selected_experience['Description'], text_area_height)
        start_date = st.date_input("Start Date", selected_experience['StartDate'])
        end_date = st.date_input("End Date", selected_experience['EndDate'])

        submitted = st.button("Update Work Experience")

        if submitted:
            upsert_experience(db_path, PersonId, selected_org_id, exp_jobtitle, exp_shortdesc,
                            exp_description, start_date, end_date, selected_language_id)
            st.success("Work Experience successfully added/updated!")


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
st.write("## Translate Work Experience Details")

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
if exp_jobtitle and exp_shortdesc and exp_description and deeplapikey:
    translated_jobtitle = deepl_client.translate_text(exp_jobtitle, source_lang=source_lang, target_lang=target_lang)
    translated_shortdesc = deepl_client.translate_text(exp_shortdesc, source_lang=source_lang, target_lang=target_lang)
    translated_description = deepl_client.translate_text(exp_description, source_lang=source_lang, target_lang=target_lang)

    edited_jobtitle = st.text_input("Translated job title:", translated_jobtitle)
    edited_shortdesc = st.text_input("Translated description in one sentence:", translated_shortdesc)
    edited_description = st.text_area("Translated full description:", translated_description, text_area_height)

    addtransbutton = st.button("Add Translated Work Experience Details")

    # Verwerk het formulier
    if addtransbutton:
        upsert_experience(db_path, PersonId, selected_org_id, edited_jobtitle, edited_shortdesc,
                                edited_description, start_date, end_date, dest_language_id)
        st.success("Translated work experience details successfully added!")
