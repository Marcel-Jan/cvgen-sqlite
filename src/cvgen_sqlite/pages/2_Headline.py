""" Introduction page
"""
import streamlit as st
from utils.database import fetch_introduction, fetch_languages, upsert_introduction
# from utils.llm import llmchat
import deepl
# import openai


# Path to database and templates
db_path = st.session_state.database
deeplapikey = st.session_state.deeplapikey
deepl_client = deepl.DeepLClient(deeplapikey)
# openai_key = st.session_state.openai_key

# Titel van de app
st.title("Resume - Headline")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: {PersonName}")

st.markdown("Use this form to add or change the introduction of your resume.")


# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id


# Fetch list of all languages
languages = fetch_languages(db_path)
language_names = [language['LanguageName'] for language in languages]

# Streamlit multiselect for language selection
selected_language = st.selectbox(
    'Select the language of your resume:',
    options=language_names
)

# Get the language ID for the selected language. It is just one value, not a list.
selected_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == selected_language][0]

# Fetch introduction text
introduction = fetch_introduction(db_path, PersonId, selected_language_id)

text_area_height = 500
st.write("## Headline")
introtext = st.text_area("Resume headline:", introduction['IntroductionText'], text_area_height)

# Submit-knop
submitted = st.button("Update Headline")

# Verwerk het formulier
if submitted:
    upsert_introduction(db_path, PersonId, introtext, selected_language_id)
    st.success("Headline successfully updated!")



# Translate introduction
st.markdown("### Translate your headline to another language")

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

# translated_intro = GoogleTranslator(source=source_lang, target=target_lang).translate(introduction['IntroductionText'])
translated_intro = deepl_client.translate_text(introtext, source_lang=source_lang, target_lang=target_lang)
translated_introtext = st.text_area("Translated resume headline:", translated_intro, text_area_height)

# Save translated introduction
st.write("### Save translated headline")
saveintro = st.button("Save translated headline")

if saveintro:
    upsert_introduction(db_path, PersonId, translated_introtext, dest_language_id)
    st.success("Translated headline successfully saved!")
