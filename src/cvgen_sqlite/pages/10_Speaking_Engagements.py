""" Managing additional activities
"""
import streamlit as st
from utils.database import fetch_languages, fetch_speaking
from utils.database import upsert_speaking
import datetime


# Path to database and templates
db_path = st.session_state.database

# Titel van de app
st.title("Speaking Engagements")

selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form for speaking engagements on your resume.")

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id

speakingengagements = fetch_speaking(db_path, PersonId)

# Dropdown menu for selecting the speaking engagement
speech_names = [speech['Title'] for speech in speakingengagements]
# Add option for new activity
speech_names.append("New activity")
selected_speechname = st.selectbox(
    'Select a speaking engagement:',
    options=speech_names
)

if selected_speechname == "New activity":
    upsert_title = st.text_input("Title", "")
    upsert_event = st.text_input("Event", "")
    upsert_eventdate = st.date_input("Date of speaking engagement", min_value=datetime.date(2011, 2, 17))

    # Submit-knop
    submitted = st.button("Add New Speaking Engagement")

else:
    # Show ActivityName for the selected activity
    selected_activity_id = [speech['SpeakingId'] for speech in speakingengagements if speech['Title'] == selected_speechname]

    # Get activity details for selected activity. It should not be a list.
    selected_speechdetails = [speech for speech in speakingengagements if speech['Title'] == selected_speechname][0]
    upsert_title = st.text_input("Title", selected_speechdetails["Title"])
    upsert_event = st.text_input("Event", selected_speechdetails["Event"])
    upsert_eventdate = st.date_input("Date of speaking engagement", selected_speechdetails["SpeakingDate"], min_value=selected_speechdetails["SpeakingDate"])

    # Submit-knop
    submitted = st.button("Update Speaking Engagement")

# Verwerk het formulier
if submitted:
    upsert_speaking(db_path, PersonId, upsert_title, upsert_event,
                    upsert_eventdate)
    st.success("Speaking engagement successfully added/updated!")

# Show Speaking Engagements
st.write("### Your list of speaking engagements:")
speakinglist = fetch_speaking(db_path, PersonId)

# Remove columns from the list
for speaking in speakinglist:
    del speaking['SpeakingId']
    # del speaking['Activities']
    del speaking['EventYear']
st.table(speakinglist)