""" Managing additional activities
"""
import streamlit as st
from utils.database import fetch_languages, fetch_publications
from utils.database import upsert_publications
import datetime


# Path to database and templates
db_path = st.session_state.database

# Titel van de app
st.title("Publications")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form to add publications to your resume.")

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id

publications = fetch_publications(db_path, PersonId)

# Dropdown menu for selecting the publication
publication_names = [publication['PublicationName'] for publication in publications]
# Add option for new activity
publication_names.append("New publication")
selected_publicationname = st.selectbox(
    'Select a publication:',
    options=publication_names
)

if selected_publicationname == "New publication":
    publication_name = st.text_input("Publication Name", "")
    publication_type = st.text_input("Publication Type", "")
    publication_author = st.text_input("Author(s)", "")
    publication_date = st.date_input("Publication Date", min_value=datetime.date(2011, 2, 17))
    publication_link = st.text_input("Link to Publication", "")
    publisher = st.text_input("Publisher", "")
    journal_volume = st.text_input("Journal Volume", "")
    journal_number = st.text_input("Journal Number", "")
    journal_pages = st.text_input("Journal: page numbers (start to end)", "")

    # Submit-knop
    submitted = st.button("Add New Publication")

else:
    # Show ActivityName for the selected activity
    selected_publication_id = [publication['PublicationId'] for publication in publications if publication['PublicationName'] == selected_publicationname]

    # Get activity details for selected activity. It should not be a list.
    selected_pubdetails = [publication for publication in publications if publication['PublicationName'] == selected_publicationname][0]
    publication_name = st.text_input("Publication Name", selected_pubdetails["PublicationName"])
    publication_type = st.text_input("Publication Type (book, journal, blogpost)", selected_pubdetails["PublicationType"])
    publication_author = st.text_input("Author(s)", selected_pubdetails["Author"])
    publication_date = st.date_input("Publication Date", selected_pubdetails["PublicationDate"],
                                     min_value=selected_pubdetails["PublicationDate"])
    publication_link = st.text_input("Link to Publication", selected_pubdetails["PublicationLink"])
    publisher = st.text_input("Publisher", selected_pubdetails["Publisher"])
    journal_volume = st.text_input("Journal Volume", selected_pubdetails["JournalVolume"])
    journal_number = st.text_input("Journal Number", selected_pubdetails["JournalNumber"])
    journal_pages = st.text_input("Journal: page numbers (start to end)", selected_pubdetails["JournalPages"])

    # Submit-knop
    submitted = st.button("Update Publication Details")

# Verwerk het formulier
if submitted:
    upsert_publications(db_path, PersonId, publication_name, publication_type, publication_author,
                        publication_date, publication_link, publisher, journal_volume, journal_number,
                        journal_pages)
    st.success("Publication successfully added/updated!")

# Show Publications
st.write("### Your list of publications:")
publist = fetch_publications(db_path, PersonId)

# Remove columns from the list
for pub in publist:
    del pub['PublicationId']
    # del pub['Activities']
    # del pub['EventYear']
st.table(publist)