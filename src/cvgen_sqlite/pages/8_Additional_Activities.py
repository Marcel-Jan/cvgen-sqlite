""" Managing additional activities
"""
import streamlit as st
from utils.database import fetch_languages, fetch_activities
from utils.database import upsert_activity
import datetime
import deepl


# Path to database and templates
db_path = st.session_state.database
deeplapikey = st.session_state.deeplapikey
deepl_client = deepl.DeepLClient(deeplapikey)

# Titel van de app
st.title("Additional activites")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form for additional activities on your resume.")

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


activities = fetch_activities(db_path, PersonId, selected_language_id)
# st.write(activities)

# Dropdown menu for selecting the activity
activity_names = [activity['ActivityName'] for activity in activities]
# Add option for new activity
activity_names.append("New activity")
selected_activityname = st.selectbox(
    'Select an activity:',
    options=activity_names
)

if selected_activityname == "New activity":
    upsert_activityname = st.text_input("Activity name", "")
    upsert_description = st.text_area("Description", "")
    upsert_startdate = st.date_input("StartDate", min_value=datetime.date(2011, 2, 17))
    upsert_enddate = st.date_input("EndDate", value=None)

    # Submit-knop
    submitted = st.button("Add New Activity")

else:
    # Show ActivityName for the selected activity
    selected_activity_id = [activity['ActivityId'] for activity in activities if activity['ActivityName'] == selected_activityname]

    # Get activity details for selected activity. It should not be a list.
    selected_activity = [activity for activity in activities if activity['ActivityName'] == selected_activityname][0]
    upsert_activityname = st.text_input("Activity name", selected_activity["ActivityName"])
    upsert_description = st.text_area("Description", selected_activity["Description"])
    upsert_startdate = st.date_input("StartDate", selected_activity["StartDate"], min_value=selected_activity["StartDate"])
    upsert_enddate = st.date_input("EndDate", selected_activity["EndDate"])

    # Submit-knop
    submitted = st.button("Update Activity")

# Verwerk het formulier
if submitted:
    upsert_activity(db_path, PersonId, upsert_activityname, upsert_description,
                    upsert_startdate, upsert_enddate, selected_language_id)
    st.success("Activity successfully added/updated!")


# Translate introduction
st.markdown("### Translate your activity to another language")

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
try:
    translated_activityname = deepl_client.translate_text(upsert_activityname, source_lang=source_lang, target_lang=target_lang)
    translated_description = deepl_client.translate_text(upsert_description, source_lang=source_lang, target_lang=target_lang)
    edited_activityname = st.text_area("Translated activity name:", translated_activityname)
    edited_description = st.text_area("Translated description:", translated_description)
except ValueError:
    pass

addactbutton = st.button("Add Activity")

# Verwerk het formulier
if addactbutton:
    upsert_activity(db_path, PersonId, edited_activityname, edited_description,
                    upsert_startdate, upsert_enddate, dest_language_id)
    st.success("Activity successfully added!")

# Show Activities
st.write("### Your list of additional activities:")
activitylist = fetch_activities(db_path, PersonId, selected_language_id)

# Remove columns from the list
for activity in activitylist:
    del activity['ActivityId']
    # del pub['Activities']
    del activity['StartYear']
st.table(activitylist)
