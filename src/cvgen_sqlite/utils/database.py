import sqlite3
from datetime import datetime


def create_tables(db_path, ddl_script):
    """Create the tables in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get content from the ddl_script
    with open(ddl_script, 'r') as f:
        # print(ddl_script)
        ddl_script_content = f.read()
        # print(ddl_script_content)
    
    try:
        cursor.executescript(ddl_script_content)
    except sqlite3.OperationalError as e:
        print(f"create_tables OperationalError: {e}")
        # If the table already exists, run the script again
        if "table Person already exists" in str(e):
            output = cursor.executescript(ddl_script_content)
            print(f"create_tables retry: {output}")
        else:
            print(f"create_tables retry failed: {e}")
    except sqlite3.IntegrityError as e:
        print(f"create_tables IntegrityError: {e}")
    except sqlite3.ProgrammingError as e:
        print(f"create_tables ProgrammingError: {e}")
    except sqlite3.Error as e:
        print(f"create_tables Other Error: {e}")
    conn.commit()
    conn.close()


def initialize_tables(db_path, ins_script, ins_countries_script):
    """Insert initial data into the tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get content from the dml_script
    with open(ins_script, 'r') as f:
        ins_script = f.read()
    print("initialize_tables")
    # print(ins_script)
    
    try:
        cursor.executescript(ins_script)
    except sqlite3.OperationalError as e:
        print(f"initialize_tables: {e}")
    except sqlite3.IntegrityError as e:
        print(f"initialize_tables: {e}")
    except sqlite3.ProgrammingError as e:
        print(f"initialize_tables: {e}")
    except sqlite3.Error as e:
        print(f"initialize_tables: {e}")
        # Stop

    with open(ins_countries_script, 'r') as f:
        ins_countries_script = f.read()
    
    try:
        cursor.executescript(ins_countries_script)
    except sqlite3.OperationalError as e:
        print(f"initialize_tables: {e}")
    except sqlite3.IntegrityError as e:
        print(f"initialize_tables: {e}")
    except sqlite3.ProgrammingError as e:
        print(f"initialize_tables: {e}")
    except sqlite3.Error as e:
        print(f"initialize_tables: {e}")

    conn.commit()
    conn.close()


# Languages
def fetch_languages(db_path):
    """Fetch a list of all languages."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    lang_query = """
        SELECT LanguageId, LanguageName, LanguageCodeISO639_1
        FROM ResumeLanguage
    """
    cursor.execute(lang_query)
    languages = cursor.fetchall()
    conn.close()
    return [{"LanguageId": row[0], "LanguageName": row[1],
             "LanguageCodeISO639_1": row[2]} for row in languages]


def fetch_countries(db_path, language_id):
    """Fetch a list of all countries."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    country_query = """
        SELECT CountryId, CountryName, Nationality
        FROM Countries
        WHERE LanguageId = ?
    """
    cursor.execute(country_query, (language_id,))
    countries = cursor.fetchall()
    conn.close()
    return [{"CountryId": row[0], "CountryName": row[1], "Nationality": row[2]}
            for row in countries]


def fetch_nationalityid(db_path, nationality, language_id):
    """Fetch the Nationality ID for a given
       country name and language id."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    country_query = """
        SELECT CountryId
        FROM Countries
        WHERE Nationality = ?
        AND LanguageId = ?
    """
    cursor.execute(country_query, (nationality, language_id))
    country_id = cursor.fetchone()
    conn.close()
    return country_id[0] if country_id else None


# Persons
def fetch_personnames(db_path):
    """Fetch a list of all persons."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    person_query = """
        SELECT PersonId, Name
        FROM Person
    """
    try:
        cursor.execute(person_query)
        persons = cursor.fetchall()
    except sqlite3.OperationalError as e:
        if "no such table: Person" in str(e):
            # Apparently the tables do not exist yet
            print("Tables do not exist yet. Creating tables.")
            create_tables(db_path, "sql/cvgen_ddl.sql")
            print("Initializing tables.")
            initialize_tables(db_path, "sql/cvgen_ins.sql", "sql/ins_countries.sql")
            cursor.execute(person_query)
            persons = cursor.fetchall()
        else:
            print(f"fetch_personnames other OperationalError: {e}")
    except sqlite3.Error as e:
        print(f"fetch_personnames sqlite3.Error: {e}")
    except Exception as e:
        print(f"fetch_personnames Exception: {e}")
    cursor.execute(person_query)
    persons = cursor.fetchall()
    conn.close()
    return [{"PersonId": row[0], "Name": row[1]} for row in persons]


def fetch_personbyid(db_path, person_id):
    """Fetch a list of all persons."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    person_query = """
        SELECT PersonId, Name, LinkToImage, LinkToVideo
        FROM Person
        WHERE PersonId = ?
    """
    cursor.execute(person_query, (person_id,))
    persons = cursor.fetchall()
    conn.close()
    return [{"PersonId": row[0], "Name": row[1]
             , "LinkToImage": row[2], "LinkToVideo": row[3]}
               for row in persons]


def fetch_personid_byname(db_path, person_name):
    """Fetch the person ID for a given person name."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT PersonId FROM Person WHERE Name = ?", (person_name,))
    person_id = cursor.fetchone()
    conn.close()
    return person_id[0] if person_id else None


def add_user(db_path, Name, LinkToImage, LinkToVideo):
    """Insert a new user into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Person (Name, LinkToImage, LinkToVideo)
        VALUES (?, ?, ?)
    """, (Name, LinkToImage, LinkToVideo))
    conn.commit()
    conn.close()


# Contact info
def fetch_contact(db_path, person_id, language_id):
    """Fetch contact details for the candidate."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    contact_query = """
        SELECT strftime('%Y', Birthday) AS BirthYear,
               c.Nationality, Residence, Email, Phone
        FROM PersonContact pc 
        INNER JOIN Countries c ON c.CountryId = pc.NationalityId
                    AND c.LanguageId = pc.LanguageId 
        WHERE pc.PersonId = ?
        AND pc.LanguageId = ?
    """
    cursor.execute(contact_query, (person_id, language_id))
    contact_details = cursor.fetchone()
    print(f"fetch_contact: {contact_details}")
    conn.close()
    return {
        "BirthYear": contact_details[0],
        "Nationality": contact_details[1],
        "Residence": contact_details[2],
        "Email": contact_details[3],
        "Phone": contact_details[4],
    }


def add_contact(db_path, PersonId, Birthday, Nationality,
                Residence, Email, Phone, LanguageId):
    """Insert a new contact details into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    nationalityid = fetch_nationalityid(db_path, Nationality, LanguageId)

    contact_query = """
        INSERT INTO PersonContact
            (PersonId, Birthday, NationalityId, Residence,
             Email, Phone, LanguageId)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(contact_query, (PersonId, Birthday, nationalityid,
                                   Residence, Email, Phone, LanguageId))
    conn.commit()
    conn.close()


# Organisations
def fetch_organisations(db_path):
    """Fetch a list of all project organisations."""
    # PersonId might need to be added.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    org_query = """
        SELECT ProjectOrganisationId, OrganisationName, Department
        FROM ProjectOrganisation
    """
    cursor.execute(org_query)
    languages = cursor.fetchall()
    conn.close()
    return [{"ProjectOrganisationId": row[0], "OrganisationName": row[1],
             "Department": row[2]} for row in languages]


def fetch_organisation_id(db_path, OrganisationName):
    """Fetch the organisation ID for a given organisation name."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    org_query = """
        SELECT ProjectOrganisationId 
        FROM ProjectOrganisation
        WHERE OrganisationName = ?
    """
    cursor.execute(org_query, (OrganisationName,))
    organisation_id = cursor.fetchone()
    conn.close()
    return organisation_id[0] if organisation_id else None


def add_organisation(db_path, OrganisationName, Department):
    """Add a project organisation."""
    # PersonId might need to be added.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    existing_organisations = fetch_organisations(db_path)

    if OrganisationName in [organisation['OrganisationName'] for organisation in existing_organisations]:
        return

    insert_statement = """
        INSERT INTO ProjectOrganisation
          (OrganisationName, Department)
        VALUES (?, ?)
    """
    result = cursor.execute(insert_statement, (OrganisationName, Department))
    conn.commit()
    conn.close()


# Education
def fetch_educations(db_path, PersonId, LanguageId):
    """Fetch a list of all education entries."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    education_query = """
        SELECT EducationId, Degree, Institution, FieldOfStudy, GraduationDate, Description,
               Activities, substr(GraduationDate, 1, 4) AS GraduationYear
        FROM Education 
        WHERE PersonId = ?
        AND LanguageId = ?
        ORDER BY GraduationDate DESC
    """
    cursor.execute(education_query, (PersonId, LanguageId))
    educations = cursor.fetchall()
    conn.close()
    return [{"EducationId": row[0], "Degree": row[1], "Institution": row[2],
             "FieldOfStudy": row[3], "GraduationDate": row[4], "Description": row[5],
             "Activities": row[6], "GraduationYear": row[7]} for row in educations]


def fetch_education(db_path, EducationId):
    """Fetch a single education entry."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    education_query = """
        SELECT Degree, Institution, FieldOfStudy, GraduationDate, Description,
               Activities
        FROM Education 
        WHERE EducationId = ?
    """
    cursor.execute(education_query, (EducationId,))
    education = cursor.fetchone()
    conn.close()
    return {
        "Degree": education[0], "Institution": education[1],
        "FieldOfStudy": education[2], "GraduationDate": education[3],
        "Description": education[4], "Activities": education[5]
    }


def add_education(db_path, PersonId, Degree, Institution, FieldOfStudy, GraduationDate, Description, Activities, LanguageId):
    """Insert a new education entry into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Education
                   (PersonId, Degree, Institution, FieldOfStudy, GraduationDate, 
                    Description, Activities, LanguageId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (PersonId, Degree, Institution, FieldOfStudy, GraduationDate, Description, Activities, LanguageId))
    conn.commit()
    conn.close()


def upsert_education(db_path, PersonId, Degree, Institution, FieldOfStudy, GraduationDate, Description, Activities, LanguageId):
    """Update or insert a new education entry."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the education already exists
    education_id = cursor.execute("""
        SELECT EducationId
        FROM Education 
        WHERE PersonId = ?
        AND Institution = ?
        AND Degree = ?
        AND LanguageId = ?
    """, (PersonId, Institution, Degree, LanguageId))
    education_id = education_id.fetchone()

    if education_id:
        # Update the existing education entry
        cursor.execute("""
            UPDATE Education 
            SET Degree = ?, FieldOfStudy = ?, GraduationDate = ?, Description = ?, Activities = ?
            WHERE EducationId = ?
        """, (Degree, FieldOfStudy, GraduationDate, Description, Activities, education_id[0]))
    else:
        # Insert a new education entry
        cursor.execute("""
            INSERT INTO Education
                       (PersonId, Degree, Institution, FieldOfStudy, GraduationDate,
                        Description, Activities, LanguageId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (PersonId, Degree, Institution, FieldOfStudy, GraduationDate,
              Description, Activities, LanguageId))
    conn.commit()
    conn.close()


# Certifications
def fetch_certifications(db_path, PersonId, StartYear=None):
    """Fetch a list of all certifications."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    certification_query = """
        SELECT CertificationId, CertificationName, Institution, IssueDate, ExpiryDate,
               EarningCriteria, CredentialLink, substr(IssueDate, 1, 4) AS IssueYear
        FROM Certification 
        WHERE PersonId = ?
        AND substr(IssueDate, 1, 4) > ?
        AND (ExpiryDate IS NULL OR ExpiryDate > datetime('now'))
        ORDER BY IssueDate DESC
    """
    cursor.execute(certification_query, (PersonId, (datetime.now().year-10)))
    certifications = cursor.fetchall()
    conn.close()
    return [{"CertificationId": row[0], "CertificationName": row[1], "Institution": row[2],
             "IssueDate": row[3], "ExpiryDate": row[4], "EarningCriteria": row[5],
             "CredentialLink": row[6], "IssueYear": row[7]} for row in certifications]


def add_certification(db_path, PersonId, CertificationName, Institution, IssueDate, ExpiryDate, EarningCriteria, CredentialLink):
    """Insert a new certification entry into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Certification (PersonId, CertificationName, Institution, 
                   IssueDate, ExpiryDate, EarningCriteria, CredentialLink)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (PersonId, CertificationName, Institution, IssueDate, ExpiryDate, EarningCriteria, CredentialLink))
    conn.commit()
    conn.close()


# Projects
def add_project(db_path, PersonId, OrganisationName, ProjectName, RoleTitle, YourRole, ProudOf, StartDate, EndDate, Purpose, LanguageId):
    """Insert a new project entry into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get OrganisationId
    OrganisationId = fetch_organisation_id(db_path, OrganisationName)

    # Add project
    insert_project_statement = """
        INSERT INTO Project (OrganisationId, ProjectName, LanguageId)
        VALUES (?, ?, ?)
    """

    cursor.execute(insert_project_statement, (OrganisationId, ProjectName, LanguageId))
    print(f"OrganisationId: {OrganisationId}")
    conn.commit()

    # Get the project ID for the new project
    projectid_query = """
        SELECT ProjectId
        FROM Project 
        WHERE ProjectName = ?
    """
    projectid = cursor.execute(projectid_query, (ProjectName,))
    projectid = projectid.fetchone()[0]
    print(f"ProjectId: {projectid}")

    # # Add project role
    cursor.execute("""
        INSERT INTO ProjectRole (ProjectID, ProjectRoleName, ProjectRoleText,
                   ProudOf, PersonId, StartDate, EndDate, Purpose, LanguageId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (projectid, RoleTitle, YourRole, ProudOf, PersonId, StartDate, EndDate, Purpose, LanguageId))

    conn.commit()
    conn.close()


def fetch_projectid(db_path, OrganisationId, ProjectName, LanguageId):
    """Fetch the project ID for a given project name."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT ProjectId
                    FROM Project
                    WHERE OrganisationId = ?
                    AND ProjectName = ?
                    AND LanguageId = ?
                   """, 
                   (OrganisationId, ProjectName, LanguageId))
    project_id = cursor.fetchone()
    print(f"ProjectId: {project_id} in fetch_projectid")
    conn.close()
    return project_id[0] if project_id else None


def fetch_projectroleid(db_path, ProjectId, PersonId, RoleTitle, LanguageId):
    """Fetch the project role ID for a given project and person."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT ProjectRoleId 
                   FROM ProjectRole 
                   WHERE ProjectId = ?
                   AND PersonId = ?
                   AND LanguageId = ?
                   AND ProjectRoleName = ?""", 
                   (ProjectId, PersonId, LanguageId, RoleTitle))

    project_role_id = cursor.fetchone()
    conn.close()
    return project_role_id[0] if project_role_id else None


def upsert_projectrole(db_path, PersonId, OrganisationId, ProjectName, RoleTitle,
                       YourRole, ProudOf, StartDate, EndDate, Purpose, LanguageId):
    """Update or insert a new project."""
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()

    # Check if the project already exists
    project_id = fetch_projectid(db_path, OrganisationId, ProjectName, LanguageId)

    # Update project
    if project_id is not None:
        # Update the existing project
        cursor.execute("""
            UPDATE Project
            SET ProjectName = ?,
                OrganisationId = ?
            WHERE ProjectId = ?
        """, (ProjectName, OrganisationId, project_id))
    else:
        # Insert a new project
        cursor.execute("""
            INSERT INTO Project (OrganisationId, ProjectName, LanguageId)
            VALUES (?, ?, ?)
        """, (OrganisationId, ProjectName, LanguageId))
        conn.commit()

        # Get project_id for the new project
        project_id = fetch_projectid(db_path, OrganisationId, ProjectName, LanguageId)

        # Insert a new project role
        cursor.execute("""
            INSERT INTO ProjectRole (ProjectId, ProjectRoleName, ProjectRoleText,
                       ProudOf, PersonId, StartDate, EndDate, Purpose, LanguageId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, RoleTitle, YourRole, ProudOf, PersonId, StartDate, EndDate, Purpose, LanguageId))
        conn.commit()

        # Get the project role id
        project_role_id = fetch_projectroleid(db_path, project_id, PersonId, RoleTitle, LanguageId)

    project_role_id = fetch_projectroleid(db_path, project_id, PersonId, RoleTitle, LanguageId)

    # Update project role
    if project_role_id is not None:
        # Update the existing project role
        cursor.execute("""
            UPDATE ProjectRole
            SET ProjectRoleName = ?,
                ProjectRoleText = ?,
                ProudOf = ?,
                StartDate = ?,
                EndDate = ?,
                Purpose = ?
            WHERE ProjectRoleId = ?
        """, (RoleTitle, YourRole, ProudOf, StartDate, EndDate, Purpose, project_role_id))

    conn.commit()
    conn.close()


def fetch_projects(db_path, LanguageId):
    """Fetch a list of all projects."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    project_query = """
        SELECT ProjectId, ProjectName, OrganisationId
        FROM Project
        WHERE LanguageId = ?
    """

    cursor.execute(project_query, (LanguageId,))
    projects = cursor.fetchall()
    conn.close()
    return [{"ProjectId": row[0], "ProjectName": row[1], "OrganisationId": row[2]} for row in projects]


# AANPASSEN: DATEADD etc..
def fetch_projects_limityears(db_path, person_id, language_id=1, project_years_back=5):
    """Fetch a list of all projects for the given resume_id."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query with projects for which the applicant had a role in the last x years
    project_query = f"""
    SELECT pro.ProjectId , ProjectName || ' (' || po.OrganisationName || ')' AS ProjectName
    FROM Project pro
    INNER JOIN ResumeLanguage rl ON rl.LanguageId = pro.LanguageId 
    INNER JOIN ProjectOrganisation po ON po.ProjectOrganisationId = pro.OrganisationId 
    INNER JOIN ProjectRole pr ON pr.ProjectId = pro.ProjectId 
	   					      AND rl.LanguageId = pr.LanguageId 
    WHERE (pr.EndDate > DATE('now', '-{project_years_back} years')
           OR pr.EndDate IS NULL)
    AND rl.LanguageId = ?
    AND pr.PersonId = ?
    """

    cursor.execute(project_query, (language_id, person_id))
    projects = cursor.fetchall()
    conn.close()
    return [{"ProjectId": row[0], "ProjectName": row[1]} for row in projects]


def fetch_project_and_roles(db_path, PersonId, LanguageId):
    """Fetch a list of all project roles for a given person."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    project_role_query = """
        SELECT 
            pro.ProjectId AS ProjectId,
            pro.ProjectName AS ProjectName,
            pro.OrganisationId AS OrganisationId,
            pr.ProjectRoleId AS ProjectRoleId,
            pr.ProjectRoleName AS ProjectRoleName,
            pr.ProjectRoleText,
            pr.ProudOf,
            pr.Purpose,
            pr.StartDate,
            pr.EndDate 
        FROM Project pro
        INNER JOIN ProjectRole pr ON pr.ProjectId = pro.ProjectId 
                                AND rl.LanguageId = pr.LanguageId 
        INNER JOIN ResumeLanguage rl ON rl.LanguageId = pro.LanguageId
        WHERE pr.PersonId = ?
        AND rl.LanguageId = ?
    """
    cursor.execute(project_role_query, (PersonId, LanguageId))
    projectroles = cursor.fetchall()
    conn.close()
    return [{"ProjectId": row[0], "ProjectName": row[1], "OrganisationId": row[2], 
             "ProjectRoleId": row[3], "ProjectRoleName": row[4], "ProjectRoleText": row[5],
             "ProudOf": row[6], "Purpose": row[7], "StartDate": row[8], "EndDate": row[9]
             } for row in projectroles]


def fetch_projectroles_for_org(db_path, PersonId, OrganisationName, LanguageId):
    """Fetch a list of all project roles for a given person and organisation."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    organisationid = fetch_organisation_id(db_path, OrganisationName)

    project_role_query = """
        SELECT 
            pro.ProjectId AS ProjectId,
            pro.ProjectName AS ProjectName,
            pro.OrganisationId AS OrganisationId,
            pr.ProjectRoleId AS ProjectRoleId,
            pr.ProjectRoleName AS ProjectRoleName,
            pr.ProjectRoleText,
            pr.ProudOf,
            pr.Purpose,
            pr.StartDate,
            pr.EndDate 
        FROM Project pro
        INNER JOIN ProjectRole pr ON pr.ProjectId = pro.ProjectId 
        INNER JOIN ResumeLanguage rl ON rl.LanguageId = pro.LanguageId
                                            AND rl.LanguageId = pr.LanguageId 
        WHERE pr.PersonId = ?
        AND rl.LanguageId = ?
        AND pro.OrganisationId = ?
    """
    cursor.execute(project_role_query, (PersonId, LanguageId, organisationid))
    projectroles = cursor.fetchall()
    conn.close()
    return [{"ProjectId": row[0], "ProjectName": row[1], "OrganisationId": row[2], 
             "ProjectRoleId": row[3], "ProjectRoleName": row[4], "ProjectRoleText": row[5],
             "ProudOf": row[6], "Purpose": row[7], "StartDate": row[8], "EndDate": row[9]
             } for row in projectroles]


def fetch_skills(db_path, PersonId, LanguageId):
    """Fetch a list of all skills."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    skill_query = """ 
        SELECT sc.CategoryName, SkillName, Level
        FROM Skill s 
        INNER JOIN SkillCategory sc ON s.SkillCategoryId = sc.SkillCategoryId 
        INNER JOIN Person per ON per.PersonId = s.PersonId
        INNER JOIN ResumeLanguage rl ON rl.LanguageId = s.LanguageId
                                        AND sc.LanguageId = rl.LanguageId 
        WHERE per.PersonId = ?
        AND rl.LanguageId = ?
        ORDER BY sc.SkillCategoryId, s.SkillId
    """

    cursor.execute(skill_query, (PersonId, LanguageId))
    skilldetails = cursor.fetchall()
    conn.close()
    return [{"CategoryName": row[0], "SkillName": row[1], "Level": row[2]} for row in skilldetails]


def fetch_skillcategories(db_path, LanguageId):
    """Fetch a list of all skill categories."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT SkillCategoryId, CategoryName
                   FROM SkillCategory
                   WHERE LanguageId = ?""",
                   (LanguageId,))
    categories = cursor.fetchall()
    conn.close()
    return [{"SkillCategoryId": row[0], "CategoryName": row[1]} for row in categories]


def update_skills(db_path, PersonId, SkillName, Level):
    """Update the skill level for a given skill."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the SkillId for the given skill
    # Can be multiple skill_ids for multiple languages
    skill_id = cursor.execute("""
        SELECT SkillId
        FROM Skill 
        WHERE PersonId = ? AND SkillName = ?
    """, (PersonId, SkillName))
    skill_ids = [skill[0] for skill in skill_id.fetchall()]

    for skill_id in skill_ids:
        # Update the skill level
        cursor.execute("""
            UPDATE Skill
            SET Level = ? 
            WHERE SkillId = ?
        """, (Level, skill_id))
    conn.commit()
    conn.close()


def add_category(db_path, CategoryName, LanguageId):
    """Add a new category to the skills database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add the new category
    cursor.execute("""
        INSERT INTO SkillCategory (CategoryName, LanguageId)
        VALUES (?, ?)
    """, (CategoryName, LanguageId))
    conn.commit()
    conn.close()


def add_skill(db_path, PersonId, SkillName, CategoryName, Level, KeySkill, LanguageId):
    """Add a new skill to the skills database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the SkillCategoryId for the given category
    print(f"CategoryName: {CategoryName}, LanguageId: {LanguageId}")
    skill_category_id = cursor.execute("""
        SELECT SkillCategoryId
        FROM SkillCategory
        WHERE CategoryName = ? AND LanguageId = ?
    """, (CategoryName, LanguageId))
    skill_category_id = skill_category_id.fetchone()[0]

    # Add the new skill
    cursor.execute("""
        INSERT INTO Skill (PersonId, SkillName, SkillCategoryId, Level, KeySkill, LanguageId)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (PersonId, SkillName, skill_category_id, Level, KeySkill, LanguageId))
    conn.commit()
    conn.close()


def fetch_introduction(db_path, PersonId, LanguageId):
    """Fetch the introduction text for the candidate."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    introduction_query = """
        SELECT IntroductionText
        FROM ResumeIntroduction 
        WHERE PersonId = ?
        AND LanguageId = ?
    """
    cursor.execute(introduction_query, (PersonId, LanguageId))
    introduction_text = cursor.fetchone()

    # If the introduction text is not available, return an empty string
    if introduction_text is None:
        return {
            "IntroductionText": "",
        }
    conn.close()
    return {
        "IntroductionText": introduction_text[0],
    }

def fetch_introduction2(db_path, PersonId, LanguageId):
    """Fetch the introduction text for the candidate."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    introduction_query = """
        SELECT IntroductionText
        FROM ResumeIntroduction2
        WHERE PersonId = ?
        AND LanguageId = ?
    """
    cursor.execute(introduction_query, (PersonId, LanguageId))
    introduction_text = cursor.fetchone()

    # If the introduction text is not available, return an empty string
    if introduction_text is None:
        return {
            "IntroductionText": "",
        }
    conn.close()
    return {
        "IntroductionText": introduction_text[0],
    }

def update_introduction(db_path, PersonId, IntroductionColumn1Text, LanguageId):
    """Update the introduction text for the candidate."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE ResumeIntroduction 
        SET IntroductionColumn1Text = ?
        WHERE PersonId = ?
        AND LanguageId = ?
    """, (IntroductionColumn1Text, PersonId, LanguageId))
    conn.commit()
    conn.close()


def upsert_introduction(db_path, PersonId, IntroductionText, LanguageId):
    """Update or insert a new introduction."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the introduction already exists
    introduction_id = cursor.execute("""
        SELECT IntroductionId FROM ResumeIntroduction
        WHERE PersonId = ?
        AND LanguageId = ?
    """, (PersonId, LanguageId))
    introduction_id = introduction_id.fetchone()

    if introduction_id:
        # Update the existing introduction
        cursor.execute("""
            UPDATE ResumeIntroduction 
            SET IntroductionText = ?
            WHERE IntroductionId = ?
        """, (IntroductionText, introduction_id[0]))
    else:
        # Insert a new introduction
        cursor.execute("""
            INSERT INTO ResumeIntroduction (PersonId, IntroductionText, LanguageId)
            VALUES (?, ?, ?)
        """, (PersonId, IntroductionText, LanguageId))
    conn.commit()
    conn.close()
    

def fetch_activities(db_path, PersonId, LanguageId):
    """Fetch a list of all additional activities."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    activity_query = """
        SELECT ActivityId, ActivityName, Description, StartDate, EndDate, substr(StartDate, 1, 4) AS StartYear
        FROM AdditionalActivity
        WHERE PersonId = ?
        AND LanguageId = ?
        ORDER BY StartDate DESC
    """
    cursor.execute(activity_query, (PersonId, LanguageId))
    activities = cursor.fetchall()
    conn.close()
    return [{"ActivityId": row[0], "ActivityName": row[1], "Description": row[2],
             "StartDate": row[3], "EndDate": row[4], "StartYear": row[5]} for row in activities]


def upsert_activity(db_path, PersonId, ActivityName, Description, StartDate, EndDate, LanguageId):
    """Update or insert a new activity."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the activity already exists
    activity_id = cursor.execute("""
        SELECT ActivityId FROM AdditionalActivity
        WHERE PersonId = ?
        AND ActivityName = ?
        AND LanguageId = ?
    """, (PersonId, ActivityName, LanguageId))
    activity_id = activity_id.fetchone()

    if activity_id:
        # Update the existing activity
        cursor.execute("""
            UPDATE AdditionalActivity
            SET Description = ?, StartDate = ?, EndDate = ?
            WHERE ActivityId = ?
        """, (Description, StartDate, EndDate, activity_id[0]))
    else:
        # Insert a new activity
        cursor.execute("""
            INSERT INTO AdditionalActivity (PersonId, ActivityName, Description, StartDate, EndDate, LanguageId)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (PersonId, ActivityName, Description, StartDate, EndDate, LanguageId))
    conn.commit()
    conn.close()


def fetch_speaking(db_path, PersonId):
    """Fetch a list of all speaking events."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    speaking_query = """
        SELECT SpeakingId, Title, Event, SpeakingDate, substr(SpeakingDate, 1, 4) AS EventYear
        FROM SpeakingEngagement
        WHERE PersonId = ?
        ORDER BY SpeakingDate DESC
    """
    cursor.execute(speaking_query, (PersonId,))
    speeches = cursor.fetchall()
    conn.close()
    return [{"SpeakingId": row[0], "Title": row[1], "Event": row[2],
             "SpeakingDate": row[3], "EventYear": row[4]} for row in speeches]


def upsert_speaking(db_path, PersonId, Title, Event, SpeakingDate):
    """Update or insert a new speaking event."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the activity already exists
    speech_query = cursor.execute("""
        SELECT SpeakingId FROM SpeakingEngagement
        WHERE PersonId = ?
        AND Title = ?
        AND Event = ? 
    """, (PersonId, Title, Event))
    speech_id = speech_query.fetchone()

    if speech_id:
        # Update the existing speaking engagement
        cursor.execute("""
            UPDATE SpeakingEngagement
            SET Title = ?, StartDate = ?, EndDate = ?
            WHERE SpeakingId = ?
        """, (Title, Event, SpeakingDate, speech_id[0]))
    else:
        # Insert a new speaking engagement
        # The LanguageId is hardcoded to 1 for now
        cursor.execute("""
            INSERT INTO SpeakingEngagement (PersonId, Title, Event, SpeakingDate, LanguageId)
            VALUES (?, ?, ?, ?, ?)
        """, (PersonId, Title, Event, SpeakingDate, 1))
    conn.commit()
    conn.close()

def fetch_publications(db_path, PersonId):
    """Fetch a list of all publications."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    publication_query = """
        SELECT PublicationId, PublicationName, PublicationType, Author, PublicationDate,
               PublicationLink, Publisher, JournalVolume, JournalNumber, JournalPages
        FROM Publication
        WHERE PersonId = ?
        ORDER BY PublicationDate
    """
    cursor.execute(publication_query, (PersonId,))
    publications = cursor.fetchall()
    conn.close()
    return [{"PublicationId": row[0], "PublicationName": row[1], "PublicationType": row[2],
             "Author": row[3], "PublicationDate": row[4],"PublicationLink": row[5],
             "Publisher": row[6], "JournalVolume": row[6], "JournalNumber": row[7],
             "JournalPages": row[8]
             } for row in publications]


def upsert_publications(db_path, PersonId, PublicationName, PublicationType, Author,
                        PublicationDate, PublicationLink, Publisher, JournalVolume, JournalNumber,
                        JournalPages):
    """Update or insert a new publication."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the publication already exists
    publication_query = cursor.execute("""
        SELECT PublicationId FROM Publication
        WHERE PersonId = ?
        AND PublicationName = ?
    """, (PersonId, PublicationName))
    publication_id = publication_query.fetchone()

    if publication_id:
        # Update the existing publication
        cursor.execute("""
            UPDATE Publication
            SET PublicationName = ?, PublicationType = ?, Author = ?, PublicationDate = ?,
                       PublicationLink = ?, Publisher = ?, JournalVolume = ?, JournalNumber = ?, JournalPages = ?
            WHERE PublicationId = ?
        """, (PublicationName, PublicationType, Author, PublicationDate, PublicationLink,
              Publisher, JournalVolume, JournalNumber, JournalPages, publication_id[0]))
    else:
        # Insert a new publication
        cursor.execute("""
            INSERT INTO Publication (PersonId, PublicationName, PublicationType, Author,
                       PublicationDate, PublicationLink, Publisher, JournalVolume, JournalNumber,
                       JournalPages)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (PersonId, PublicationName, PublicationType, Author, PublicationDate, PublicationLink,
              Publisher, JournalVolume, JournalNumber, JournalPages))
    conn.commit()
    conn.close()


def fetch_experiences(db_path, PersonId, LanguageId, YearsBack=10):
    """Fetch a list of work experiences."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    experience_query = """
        SELECT ExperienceId, po.OrganisationName, StartDate, EndDate, JobTitle, ShortDescription,
               Description, we.LanguageId
        FROM WorkExperience we
        INNER JOIN ProjectOrganisation po ON po.ProjectOrganisationId = OrganisationId 
        WHERE we.PersonId = ?
        AND we.LanguageId = ?
        AND substr(StartDate, 1, 4) > ?
        ORDER BY StartDate DESC
    """
    cursor.execute(experience_query, (PersonId, LanguageId, (datetime.now().year-YearsBack)))
    experiences = cursor.fetchall()
    conn.close()
    return [{"ExperienceId": row[0], "OrganisationName": row[1], "StartDate": row[2],
             "EndDate": row[3], "JobTitle": row[4], "ShortDescription": row[5],
             "Description": row[6]} for row in experiences]


def fetch_experience_for_org(db_path, PersonId, OrganisationId, LanguageId):
    """Fetch a list of work experience per organisation."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    experience_query = """
        SELECT ExperienceId, OrganisationId, StartDate, EndDate, JobTitle, ShortDescription, Description, LanguageId
        FROM WorkExperience 
        WHERE PersonId = ?
        AND LanguageId = ?
        AND OrganisationId = ?
        ORDER BY StartDate DESC
    """
    cursor.execute(experience_query, (PersonId, LanguageId, OrganisationId))
    categories = cursor.fetchall()
    conn.close()
    return [{"ExperienceId": row[0], "OrganisationId": row[1], "StartDate": row[2],
             "EndDate": row[3], "JobTitle": row[4], "ShortDescription": row[5],
             "Description": row[6]} for row in categories]


def upsert_experience(db_path, PersonId, OrganisationId, JobTitle, ShortDescription,
                      Description, StartDate, EndDate, LanguageId):
    """Update or insert a new work experience entry."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the experience already exists
    experience_query = cursor.execute("""
        SELECT ExperienceId FROM WorkExperience 
        WHERE PersonId = ?
        AND OrganisationId = ?
        AND ShortDescription = ?
        AND LanguageId = ?
    """, (PersonId, OrganisationId, ShortDescription, LanguageId))
    experience_id = experience_query.fetchone()

    if experience_id:
        # Update the existing experience
        cursor.execute("""
            UPDATE WorkExperience 
            SET JobTitle = ?, ShortDescription = ?, Description = ?, StartDate = ?, EndDate = ?
            WHERE ExperienceId = ?
        """, (JobTitle, ShortDescription, Description, StartDate, EndDate, experience_id[0]))
    else:
        # Insert a new experience
        cursor.execute("""
            INSERT INTO WorkExperience (PersonId, OrganisationId, JobTitle, ShortDescription, Description, StartDate, EndDate, LanguageId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (PersonId, OrganisationId, JobTitle, ShortDescription, Description, StartDate, EndDate, LanguageId))
    conn.commit()
    conn.close()


def fetch_settings(db_path):
    """Fetch a list of all settings."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT SettingName, SettingValue
                   FROM ResumeSettings
                   """)
    settings = cursor.fetchall()
    conn.close()
    return [{"SettingName": row[0], "SettingValue": row[1]} for row in settings]


def upsert_settings(db_path, setting_name, setting_value):
    """Update or insert a new setting."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the setting already exists
    setting_query = cursor.execute("""
        SELECT count(SettingName) AS CountSettingName
        FROM ResumeSettings
        WHERE SettingName = ?
    """, (setting_name,))
    count_setting_name = setting_query.fetchone()

    if count_setting_name[0] > 0:
        # Update the existing setting
        cursor.execute("""
            UPDATE ResumeSettings
            SET SettingValue = ?
            WHERE SettingName = ?
        """, (setting_value, setting_name[0]))
    elif count_setting_name[0] == 0:
        # Insert a new setting
        cursor.execute("""
            INSERT INTO ResumeSettings (SettingName, SettingValue)
            VALUES (?, ?)
        """, (setting_name, setting_value))
    conn.commit()
    conn.close()
