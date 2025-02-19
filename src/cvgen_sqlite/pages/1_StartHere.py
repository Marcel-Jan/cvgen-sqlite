""" Start page
"""
import streamlit as st
from dotenv import set_key
from utils.database import add_user, fetch_languages, fetch_countries
from utils.database import add_contact, fetch_personid_byname, fetch_personbyid
from utils.database import upsert_settings, fetch_settings
import datetime


# Path to database and templates
db_path = st.session_state.database

# Titel van de app
st.title("Resume - Create User")
st.markdown("To create your resume you need to enter some information.")


username = st.text_input("Your name")
linktoimage = st.text_input("Link to a picture of you", placeholder="https://dikw.com/wp-content/uploads/2025/01/John-Doe-768x769.jpg")
linktovideo = st.text_input("Optional: link to a video introduction", placeholder="Link to a video introduction")

# Submit-knop
submitted = st.button("Create user")

# Verwerk het formulier
if submitted:
    add_user(db_path, username, linktoimage, linktovideo)
    st.success("Account created!")

person_id = fetch_personid_byname(db_path, username)

# Fetch list of all languages
languages = fetch_languages(db_path)
language_names = [language['LanguageName'] for language in languages]

st.title("Contact Details")

# Streamlit multiselect for language selection
selected_language = st.selectbox(
    'Select the language for your contact details:',
    options=language_names
)

# Get the language ID for the selected language. It is just one value, not a list.
selected_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == selected_language][0]


st.write("Use this form to add your contact details to your resume.")

birthdate = st.date_input("Birthdate", min_value=datetime.date(1900, 1, 1))
countries = fetch_countries(db_path, selected_language_id)
# st.write(countries)
nationalities = [country["Nationality"] for country in countries]
country_list = [country["CountryName"] for country in countries]
# st.write("Nationalities:", nationalities)

if "Nederlands" in nationalities:
    nationality_nl = nationalities.index("Nederlands")
    country_nl = country_list.index("Nederland")
elif "Dutch" in nationalities:
    nationality_nl = nationalities.index("Dutch")
    country_nl = country_list.index("Netherlands")
else:
    print("No Dutch")

nationality = st.selectbox("Nationality", nationalities, index=nationality_nl)
country = st.selectbox("Country of residence", country_list, index=country_nl)
residence = st.text_input("City of residence", placeholder="For example: Utrecht")
email = st.text_input("Email", placeholder="For example: user@domain.com")
phone = st.text_input("Phone", placeholder="For example: +31 6 12345678")

full_residence = residence + ", " + country

submitted = st.button("Add contact details")

if submitted:
    add_contact(db_path, person_id, birthdate, nationality, full_residence,
	            email, phone, selected_language_id)
    st.success("Contact details successfully added!")


# Set up settings
st.write("## API Keys")
st.write("For translation we use DeepL. You need an API key for this.")
st.write("You can get a free DeepL API key here: https://www.deepl.com/nl/pro-api#api-pricing")
deepl_apikey = st.text_input("DeepL API key (for translations).", type="password")

# Submit-knop
apisubmitted = st.button("Save API Keys")

if apisubmitted:
    set_key('.env', 'DEEPL_APIKEY', deepl_apikey)


# Choose the company logo url
st.write("### Resume settings")

settings = fetch_settings(db_path)
# st.write(settings)
# Get the company logo url
try:
    company_logo_url = settings['CompanyLogo']
except TypeError:
    company_logo_url = ""

# Set the company logo
company_logo = st.text_input("Company logo URL (to be displayed on the header.)", company_logo_url)

# Submit-knop
submitted = st.button("Save settings")

if submitted:
    # Update the settings in the database
    upsert_settings(db_path, setting_name="CompanyLogo", setting_value=company_logo)


st.write("### Current settings")
st.table(settings)
