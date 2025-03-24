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


def fetch_resume_data(db_path, person_id, language_id=None, selected_project_ids=None,
                      certificate_ids=None, **kwargs):
    """Fetch resume data and only include selected projects."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    resume_data = {
        "persons": fetch_personbyid(db_path, person_id)[0],
        "settings": fetch_settings(db_path),
        "contact": fetch_contact(db_path, person_id, language_id),
        # Remove None values from intro_texts
        "introtexts": {k: v for k, v in fetch_introduction(db_path, person_id, language_id).items() if v is not None},
        "certificates": fetch_certifications(db_path, person_id),
        "educations": fetch_educations(db_path, person_id, language_id),
    }

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
    experience_years_back = kwargs.get("experience_years_back", 10)
    experience_section = kwargs.get("experience_section", "Full")
    experiences = fetch_experiences(db_path, person_id, language_id, experience_years_back)

    # Add experience description if requested
    if experience_section == "Brief":
        for exp in experiences:
            exp.pop("Description", None)  # Veilig verwijderen zonder KeyError
    resume_data["experiences"] = experiences if experience_section != "None" else []
    resume_data["experience_section"] = experience_section

    # Optional sections
    optional_sections_with_lang = {
        "skillsadded": ("skills", fetch_skills),
        "activitiesadded": ("activities", fetch_activities),
    }

    optional_sections_without_lang = {
        "speakingadded": ("speakingengagements", fetch_speaking),
        "publicationsadded": ("publications", fetch_publications),
    }

    for key, (section, func) in optional_sections_with_lang.items():
        if kwargs.get(key, True):
            resume_data[section] = func(db_path, person_id, language_id)

    for key, (section, func) in optional_sections_without_lang.items():
        if kwargs.get(key, True):
            resume_data[section] = func(db_path, person_id)

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


with st.expander("Resume settings"):

    # AVG /GDPR compliancy
    st.write("AVG / GDPR compliancy (means leaving out personal information like phone number, mail address and your photo).")
    resume_settings = {
        "gdprcompliant": st.checkbox("Make the resume AVG / GDPR compliant.", value=False),
        "experience_section": st.selectbox("Work experience section:", ("Full", "Brief", "None"), index=0),
        "skillsadded": st.checkbox("Add skills section.", value=True),
        "activitiesadded": st.checkbox("Add activities section.", value=True),
        "speakingadded": st.checkbox("Add speaking engagements section.", value=True),
        "publicationsadded": st.checkbox("Add publications section.", value=True)
    }

    resume_settings["experience_years_back"] = (
        st.slider("How many years of work experience?", 0, 50, 10) if resume_settings["experience_section"] != "None" else 0
    )

with st.expander("Layout of the resume"):
    # Makeup of the resume
    st.write("### Resume Makeup")
    layout_settings = {
        "maincolor": st.color_picker("Header and line colour", "#0056b3"),
        "backgroundcolor": st.color_picker("Background colour", "#f9f9f9"),
        "textcolor": st.color_picker("Text colour", "#444444"),
        # "font_family": st.selectbox("Font family", ["Arial", "Times New Roman", "Courier New",
        #                                             "Verdana", "Georgia", "Roboto",
        #                                             "Open Sans", "Lato", "Montserrat"]),
        # "font_size": st.selectbox("Font size", ["x-small", "small", "medium", "large", "x-large"]),
        # "line_height": st.slider("Line height (pixels)", 1, 3, 1.5),
        "section_margin_top": st.slider("Margin top (pixels)", 0, 100, 10),
        "section_margin_bottom": st.slider("Margin bottom (pixels)", 0, 100, 10),
        "section_margin_left": st.slider("Margin left (pixels)", 0, 100, 10),
        "section_margin_right": st.slider("Margin right (pixels)", 0, 100, 10),
        "section_padding": st.slider("Padding (pixels)", 0, 100, 20),
        "section_padding_left": st.slider("Padding left (pixels)", 0, 100, 20),
        "section_padding_right": st.slider("Padding right (pixels)", 0, 100, 20),
        "section_padding_top": st.slider("Padding top (pixels)", 0, 100, 20),
        "section_padding_bottom": st.slider("Padding bottom (pixels)", 0, 100, 20),
        "section_border_left": st.slider("Border left (the vertical line) (pixels)", 0, 100, 4),
    }

# with st.expander("Preview resume data"):
#     resume_data = fetch_resume_data(
#         db_path, person_id=PersonId, language_id=selected_language_id, selected_project_ids=ordered_project_ids, **resume_settings
#     )
#     st.write(resume_data)


# Button to generate resume
if st.button('Generate Resume'):
    with st.spinner('Generating your resume...'):
        resume_data = fetch_resume_data(
            db_path, person_id=PersonId, language_id=selected_language_id, selected_project_ids=ordered_project_ids, **resume_settings
        )
        person_name = resume_data["persons"]["Name"].replace(" ", "_")
        # st.write(resume_data)
        
        px_fields = {
            "section_margin_top",
            "section_margin_bottom",
            "section_margin_left",
            "section_margin_right",
            "section_padding",
            "section_padding_left",
            "section_padding_right",
            "section_padding_top",
            "section_padding_bottom",
            "section_border_left",
        }
        # Voeg "px" toe aan de juiste instellingen
        resume_data["layout"] = {
            key: f"{value}px" if key in px_fields else value
            for key, value in layout_settings.items()
        }
        # st.write(f"Layout settings: {resume_data['layout']}")

        # Datestring for the output file
        datestring = datetime.datetime.now().strftime("%Y%m%d")

        # Output filename
        if targetorg and resume_settings["gdprcompliant"]:
            pdf_filename = f'resume_{person_name}_{selected_language}_{targetorg}_{datestring}_GDPR.pdf'
        elif targetorg:
            pdf_filename = f'resume_{person_name}_{selected_language}_{targetorg}_{datestring}.pdf'
        elif resume_settings["gdprcompliant"]:
            pdf_filename = f'resume_{person_name}_{selected_language}_{datestring}_GDPR.pdf'
        else:
            pdf_filename = f'resume_{person_name}_{selected_language}_{datestring}.pdf'

        output_path = f'output/{pdf_filename}'
        
        output_from_function, pdfdata = generate_resume_pdf(resume_data, template_path, output_path,
                                                            selected_language, resume_settings["gdprcompliant"])
        st.download_button(label="Download CV as PDF", data=pdfdata, file_name=pdf_filename, mime="application/pdf")
