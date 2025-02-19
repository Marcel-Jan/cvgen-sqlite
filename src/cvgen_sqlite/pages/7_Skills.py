""" Page 6: Skills Manager
"""
import streamlit as st
from utils.database import fetch_skills, fetch_languages, update_skills
from utils.database import add_category, add_skill, fetch_skillcategories

# Path to database and templates
db_path = st.session_state.database

# Titel van de app
st.title("Skills Manager")

# Retrieve persisted user name from session state
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")
st.markdown("Use this form to change skills in your resume.")

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

skills = fetch_skills(db_path, PersonId, selected_language_id)
all_categories = fetch_skillcategories(db_path, selected_language_id)
all_categories_list = [category['CategoryName'] for category in all_categories]

# Show skills with a category header
categories = set([skill['CategoryName'] for skill in skills])

for category in categories:
    st.write(f"### {category}")
    for skill in skills:
        if skill['CategoryName'] == category:
            # st.write(f"- {skill['SkillName']}")
            new_skilllevel = st.slider(skill['SkillName'], 0, 5, skill['Level'])

            # Update the skills list for this category
            skill['Level'] = new_skilllevel
            skills[skills.index(skill)] = skill


# Submit edited results back to database
if st.button("Update Changes"):
    # st.write("Updating changes to the database")
    for skill in skills:
        # Update the skill level in the database (for all languages)
        update_skills(db_path, PersonId, skill['SkillName'], skill['Level'])

# Add new category
st.write("## Add New Category")
new_category = st.text_input("New Category", placeholder="Add a new category")
if st.button("Add Category"):
    # st.write("Adding new category to the database")
    add_category(db_path, new_category, selected_language_id)
    st.success(f"Category '{new_category}' successfully added!")

# Add new skill
st.write("## Add New Skill")
with st.form("new_skill_form"):
    new_skill = st.text_input("Skill Name", placeholder="Add a new skill")
    new_skilllevel = st.slider("Skill Level", 0, 5, 0)
    new_skillcategory = st.selectbox("Category", list(all_categories_list), index=0)
    new_skill_key_bool = st.checkbox("Key Skill")
    # st.write(f"new_skill_key: {new_skill_key_bool}")

    # Convert new_skill_key to 0 or 1
    if new_skill_key_bool:
        new_skill_key = 1
    else:
        new_skill_key = 0
    submitted_newskill = st.form_submit_button("Add Skill")

if submitted_newskill:
    add_skill(db_path, PersonId, new_skill, new_skillcategory, new_skilllevel, new_skill_key, selected_language_id)
    st.success(f"Skill entry for '{new_skill}' successfully added!")


# Show Skills
st.write("## Skills")
skills = fetch_skills(db_path, PersonId, selected_language_id)
st.table(skills)
# Remove SkillId from the list 