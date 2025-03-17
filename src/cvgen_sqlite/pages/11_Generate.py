import streamlit as st
import sqlite3
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from streamlit_sortables import sort_items
from utils.database import fetch_languages, fetch_contact, fetch_skills, fetch_activities
from utils.database import fetch_speaking, fetch_publications, fetch_certifications
from utils.database import fetch_educations, fetch_experiences, fetch_personbyid
from utils.database import fetch_introduction, fetch_projects_limityears, fetch_settings
import datetime
import os


def fetch_resume_data(db_path, person_id=1, language_id=None,
                      selected_project_ids=None,
                      certificate_ids=None,
                      experience_years_back=10):
    """Fetch resume data and only include selected projects."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    resume_data = {}
    persons = fetch_personbyid(db_path, person_id)[0]
    resume_data['persons'] = persons

    settings = fetch_settings(db_path)
    resume_data['settings'] = settings

    # Get contact details
    contact = fetch_contact(db_path, person_id, language_id)
    # st.write(f"contact: {contact}")
    resume_data['contact'] = contact

    # Get intro text columns
    intro_texts = fetch_introduction(db_path, person_id, language_id)
    # print(f"intro_texts: {intro_texts}")
    # st.write(f"intro_texts: {intro_texts}")
    # Remove None values from intro_texts
    intro_texts = {k: v for k, v in intro_texts.items() if v is not None}
    # st.write(f"intro_texts: {intro_texts}")
    resume_data['introtexts'] = intro_texts
    # print(f"resume_data['introtexts']: {resume_data['introtexts']}")


    # Get only selected projects
    if selected_project_ids:
        placeholders = ','.join('?' for _ in selected_project_ids)
        selected_project_query = f"""
            SELECT pro.ProjectId,
                pro.ProjectName || ' (' || po.OrganisationName || ')' AS ProjectName,
                pr.ProjectRoleName AS ProjectRoleName,
                pr.Purpose,
                pr.ProjectRoleText,
                pr.ProudOf,
                pr.StartDate,
                pr.EndDate 
            FROM Project pro
            INNER JOIN ProjectRole pr ON pr.ProjectId = pro.ProjectId 
	   					  AND rl.LanguageId = pr.LanguageId 
            INNER JOIN ResumeLanguage rl ON rl.LanguageId = pro.LanguageId 
            INNER JOIN ProjectOrganisation po ON po.ProjectOrganisationId = pro.OrganisationId
            WHERE pro.ProjectId IN ({placeholders})
            AND rl.LanguageId = {language_id}
            AND pr.PersonId = {person_id}
        """
        cursor.execute(selected_project_query, selected_project_ids)
        projects = cursor.fetchall()
        ordered_projects = sorted(projects, key=lambda x: ordered_project_ids.index(x[0]))
    else:
        all_project_query = f"""
            SELECT pro.ProjectId,
                pro.ProjectName || ' (' || po.OrganisationName || ')' AS ProjectName,
                pr.ProjectRoleName AS ProjectRoleName,
                pr.Purpose,
                pr.ProjectRoleText,
                pr.ProudOf,
                pr.StartDate,
                pr.EndDate 
            FROM Project pro
            INNER JOIN ProjectRole pr ON pr.ProjectId = pro.ProjectId 
	   					  AND rl.LanguageId = pr.LanguageId 
            INNER JOIN ResumeLanguage rl ON rl.LanguageId = pro.LanguageId 
            INNER JOIN ProjectOrganisation po ON po.ProjectOrganisationId = pro.OrganisationId 
            WHERE rl.LanguageId = ?
            AND pr.PersonId = ?
        """
        cursor.execute(all_project_query, (language_id, person_id))
        projects = cursor.fetchall()
        ordered_projects = projects

    resume_data['projects'] = []

    for project in ordered_projects:
        project_data = dict(zip(['ProjectId', 'ProjectName', 'ProjectRoleName',
                                 'Purpose', 'ProjectRoleText', 'ProudOf', 'StartDate',
                                 'EndDate'], project))

        resume_data['projects'].append(project_data)
    
    # Get work experiences
    experiences = fetch_experiences(db_path, person_id, language_id, experience_years_back)
    resume_data['experiences'] = experiences

    # Get certifications
    certificates = fetch_certifications(db_path, person_id)
    resume_data['certificates'] = certificates

    # Get educations
    educations = fetch_educations(db_path, person_id, language_id)
    resume_data['educations'] = educations

    # Get skills
    skills = fetch_skills(db_path, person_id, language_id)
    resume_data['skills'] = skills

    # Get additional activities
    activities = fetch_activities(db_path, person_id, language_id)
    resume_data['activities'] = activities

    # Get speaking engagements
    speakingengagements = fetch_speaking(db_path, person_id)
    resume_data['speakingengagements'] = speakingengagements

    # Get publications
    publications = fetch_publications(db_path, person_id)
    resume_data['publications'] = publications

    conn.close()
    return resume_data


# --- PDF Generation Functions ---
def generate_resume_pdf(data, template_path, output_path, language, gdprcompliant):
    """Generate the resume PDF using Jinja2 and WeasyPrint."""
    env = Environment(loader=FileSystemLoader(template_path))
    if language == 'Nederlands':
        template = env.get_template('resume_template_nl.html')
    elif language == 'English':
        template = env.get_template('resume_template_en.html')
    else:
        print(f"Language {language} not supported. Defaulting to English.")
        template = env.get_template('resume_template_en.html')

    # Add GDPR compliant flag to data
    data['gdprcompliant'] = gdprcompliant

    # Render HTML with Jinja2
    rendered_html = template.render(data)

    # Generate PDF from HTML
    try:
        HTML(string=rendered_html).write_pdf(output_path)
    except OSError as e:
        if "No such file or directory" in str(e):
            print(f"Error: {e}")
            print("Creating output directory.")
            # Create directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            HTML(string=rendered_html).write_pdf(output_path)
    except Exception as e:
        print(f"Error: {e}")

    # Put PDF data in variable
    with open(output_path, 'rb') as pdf:
        pdfdata = pdf.read()

    print(f"PDF successfully created at: {output_path}")
    return output_path, pdfdata


# --- Streamlit App ---
st.title("Interactive Resume Builder")
selected_person = st.session_state.selected_person
PersonName = selected_person
st.write(f"### Resume for: _{PersonName}_")

st.markdown("Select the language of your resume.")

# Path to database and templates
db_path = st.session_state.database
template_path = 'templates'

# Retrieve persisted user id and name from session state
selected_person_id = st.session_state.selected_person_id
PersonId = selected_person_id

# For what organisation are we generating the resume?
st.write("Name of the organisation to which the resume is addressed")
targetorg = st.text_input("Organisation Name", value="")

# Fetch list of all languages
languages = fetch_languages(db_path)
language_names = [language['LanguageName'] for language in languages]
# print(f"Language names: {language_names}")

# Streamlit multiselect for project selection
selected_language = st.selectbox(
    'Select the language of your resume:',
    options=language_names
)

# Get the language ID for the selected language. It is just one value, not a list.
selected_language_id = [language['LanguageId'] for language in languages if language['LanguageName'] == selected_language][0]


# AVG /GDPR compliancy
st.write("AVG / GDPR compliancy (means leaving out personal information like photo, phone number, mail address and your photo).")
gdprcompliant = st.checkbox("Make the resume AVG / GDPR compliant (no photo, phone number, mail address).", value=False)

# Add slider how many years back you want to see projects.
project_years_back = st.slider('How many years back do you want to see projects?', 0, 20, 5)

# Fetch list of all projects
projects = fetch_projects_limityears(db_path, PersonId, selected_language_id, project_years_back)
project_names = [project['ProjectName'] for project in projects]

# Add header for two containers
project_items = [
                    {'header': 'Selected projects', 'items': project_names},
                    {'header': 'Unselected projects', 'items': []}
]

st.markdown("### Reorder Projects")
selected_and_unselected_projects = sort_items(project_items, multi_containers=True, direction='horizontal')

# Only select the items from the first container
ordered_project_names = selected_and_unselected_projects[0]['items']

# Map project names back to their IDs
ordered_projects = [project for name in ordered_project_names for project in projects if project['ProjectName'] == name]
ordered_project_ids = [project['ProjectId'] for project in ordered_projects if project['ProjectName'] in ordered_project_names]

# Add slider how old work experience you want.
experience_years_back = st.slider('How many years work experience do you want in your resume?', 0, 50, 10)


# Button to generate resume
if st.button('Generate Resume'):
    with st.spinner('Generating your resume...'):
        resume_data = fetch_resume_data(db_path, person_id=PersonId, 
                                        language_id=selected_language_id,
                                        selected_project_ids=ordered_project_ids,
                                        experience_years_back=experience_years_back)
        person_name = resume_data["persons"]["Name"].replace(" ", "_")
        # st.write(resume_data)
        
        # Datestring for the output file
        datestring = datetime.datetime.now().strftime("%Y%m%d")
        if targetorg and gdprcompliant:
            pdf_filename = f'resume_{person_name}_{selected_language}_{targetorg}_{datestring}_GDPR.pdf'
        elif targetorg:
            pdf_filename = f'resume_{person_name}_{selected_language}_{targetorg}_{datestring}.pdf'
        elif gdprcompliant:
            pdf_filename = f'resume_{person_name}_{selected_language}_{datestring}_GDPR.pdf'
        else:
            pdf_filename = f'resume_{person_name}_{selected_language}_{datestring}.pdf'

        output_path = f'output/{pdf_filename}'
        
        output_from_function, pdfdata = generate_resume_pdf(resume_data, template_path, output_path, selected_language, gdprcompliant)
        st.download_button(label="Download CV as PDF", data=pdfdata, file_name=pdf_filename, mime="application/pdf")
