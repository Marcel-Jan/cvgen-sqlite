import os
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path
from utils.database import fetch_personnames, fetch_contact, create_tables, initialize_tables



# Load the environment variables
load_dotenv()

# Zet de werkdirectory op de projectroot
ROOT_DIR = Path(__file__).parent.parent
db_path = 'cvgen.db'
template_path = 'templates'
db_create_script = 'sql/cvgen_ddl.sql'
DEEPL_APIKEY = os.environ.get("DEEPL_APIKEY")
db_insert_script = 'sql/cvgen_ins.sql'
ins_countries_script = 'sql/ins_countries.sql'


if 'database' not in st.session_state:
    st.session_state.database = db_path

st.session_state.database = db_path

# DeepL API key for translations
if 'deeplapikey' not in st.session_state:
    st.session_state.deeplapikey = DEEPL_APIKEY

st.session_state.deeplapikey = DEEPL_APIKEY

# Configuratie
st.set_page_config(page_title="CV Generator", page_icon="📄", layout="wide")


# Check that the database exists
if not Path(db_path).exists():
    # Create the database
    create_tables(db_path, db_create_script)
    st.write(f"Database created at {db_path}")

    # Insert data into the database
    initialize_tables(db_path, db_insert_script, ins_countries_script)



# Startpagina
st.title("CV Generator")
st.markdown("""
Welkome to the CV Generator! Use the sidebar to navigate through the pages.
""")

# Toon paden (voor debugging, optioneel)
if st.checkbox("Show file locations (for debugging)"):
    st.write(f"Root path: {ROOT_DIR}")
    st.write(f"Database path: {db_path}")
    st.write(f"Template path: {template_path}")

# Selecteer de gebruiker
# st.sidebar.title("User")

persons = fetch_personnames(db_path)

# Maak een lijst van namen
person_names = [person['Name'] for person in persons]

# Streamlit multiselect for project selection
selected_person = st.selectbox(
    'Select the user:',
    options=person_names
)

# Get the person ID for the selected person. It is just one value, not a list.
try:
    selected_person_id = [person['PersonId'] for person in persons if person['Name'] == selected_person][0]
    # Persist the user id in the session state
    if 'selected_person_id' not in st.session_state:
        st.session_state.selected_person_id = selected_person_id

    st.session_state.selected_person_id = selected_person_id

    # Persist the username in the session state
    if 'selected_person' not in st.session_state:
        st.session_state.selected_person = selected_person
    st.session_state.selected_person = selected_person

    # Toon de geselecteerde gebruiker
    st.write(f"Selected user: {selected_person}, person_id: {selected_person_id}, ID: {st.session_state.selected_person_id}")

    # Fetch contact details
    contact = fetch_contact(db_path, selected_person_id, 1)
    # st.write(f"Contact details: {contact}")
except IndexError:
    st.write("### First create your account in the 'StartHere' page.")

