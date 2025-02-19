CREATE TABLE IF NOT EXISTS Person 
	(PersonId INTEGER PRIMARY KEY,
	 Name TEXT,
	 LinkToImage TEXT,
	 LinkToVideo TEXT
);

CREATE TABLE IF NOT EXISTS ResumeLanguage 
	(LanguageId INTEGER PRIMARY KEY,
	 LanguageName TEXT,
     LanguageCodeISO639_1 TEXT
);

CREATE TABLE IF NOT EXISTS Countries (
    	CountryId INTEGER,
    	Alpha2Code TEXT,
    	Alpha3Code TEXT,
    	CountryName TEXT,
    	Nationality TEXT,
    	LanguageId INTEGER
);

CREATE TABLE IF NOT EXISTS PersonContact
	(ContactId INTEGER PRIMARY KEY,
	 PersonId INTEGER,
	 Birthday DATE,
	 NationalityId INTEGER,
	 Residence TEXT,
	 Email TEXT,
	 Phone TEXT,
	 LanguageId INTEGER,
	 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
	 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
);



CREATE TABLE IF NOT EXISTS ResumeIntroduction 
	(IntroductionId INTEGER PRIMARY KEY,
	 IntroductionText TEXT,
	 PersonId INTEGER,
	 LanguageId INTEGER,
	 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
	 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
);

CREATE TABLE IF NOT EXISTS ProjectOrganisation
	(ProjectOrganisationId INTEGER PRIMARY KEY,
	 OrganisationName TEXT,
	 Department TEXT
);



CREATE TABLE IF NOT EXISTS Project 
	(ProjectId INTEGER PRIMARY KEY,
	 ProjectName TEXT,
	 OrganisationId INTEGER,
	 LanguageId INTEGER,
	 FOREIGN KEY(OrganisationId) REFERENCES ProjectOrganisation(ProjectOrganisationId),
	 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
);


CREATE TABLE IF NOT EXISTS ProjectRole 
	(ProjectRoleId INTEGER PRIMARY KEY,
	 ProjectId INTEGER,
	 ProjectRoleName TEXT,
	 Purpose TEXT,
	 ProjectRoleText TEXT,
	 ProudOf TEXT,
	 PersonId INTEGER,
	 StartDate DATE,
	 EndDate DATE,
	 LanguageId INTEGER,
 	 FOREIGN KEY(ProjectId) REFERENCES Project(ProjectId),
 	 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 	 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
);



CREATE TABLE IF NOT EXISTS Certification 
	(CertificationId INTEGER PRIMARY KEY,
	 PersonId INTEGER,
	 CertificationName TEXT,
	 Institution TEXT,
	 IssueDate DATE,
	 ExpiryDate DATE,
	 EarningCriteria TEXT,
	 CredentialLink TEXT,
	 FOREIGN KEY(PersonId) REFERENCES Person(PersonId)
);


CREATE TABLE IF NOT EXISTS Education 
	(EducationId INTEGER PRIMARY KEY,
	 PersonId INTEGER,
	 Institution TEXT,
	 FieldOfStudy TEXT,
	 GraduationDate DATE,
	 Degree TEXT,
	 Description TEXT,
	 Activities TEXT,
	 LanguageId INTEGER,
	 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 	 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
);


-- Skills
CREATE TABLE IF NOT EXISTS SkillCategory
(SkillCategoryId INTEGER PRIMARY KEY,
 CategoryName TEXT,
 LanguageId INTEGER);

CREATE TABLE IF NOT EXISTS Skill
(SkillId INTEGER PRIMARY KEY,
 PersonId INTEGER,
 SkillName TEXT,
 SkillCategoryId INTEGER,
 Level INTEGER,
 KeySkill INTEGER,
 LanguageId INTEGER,
 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 FOREIGN KEY(SkillCategoryId) REFERENCES SkillCategories(SkillCategoryId),
 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
 );
 

-- Additional activities
CREATE TABLE IF NOT EXISTS AdditionalActivity
(ActivityId INTEGER PRIMARY KEY,
 PersonId INTEGER,
 ActivityName TEXT,
 Description TEXT,
 StartDate TEXT,
 EndDate TEXT,
 LanguageId INTEGER,
 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
 );


CREATE TABLE IF NOT EXISTS SpeakingEngagement
(SpeakingId INTEGER PRIMARY KEY,
 PersonId INTEGER,
 Title TEXT,
 Event TEXT,
 SpeakingDate TEXT,
 Link TEXT,
 LanguageId INTEGER,
 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
 );


-- Publications
CREATE TABLE IF NOT EXISTS Publication
(PublicationId INTEGER PRIMARY KEY,
 PersonId INTEGER,
 PublicationName TEXT,
 PublicationType TEXT,
 Author TEXT,
 Publisher TEXT,
 PublicationDate TEXT,
 PublicationLink TEXT,
 JournalVolume INTEGER, -- Jaargang
 JournalNumber INTEGER, -- Nummer
 JournalPages TEXT, -- Pages where to find the article
 LanguageId INTEGER,
 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
 );



-- Work experience
CREATE TABLE IF NOT EXISTS WorkExperience
(ExperienceId INTEGER PRIMARY KEY,
 PersonId INTEGER,
 OrganisationId INTEGER,
 StartDate TEXT,
 EndDate TEXT,
 JobTitle TEXT,
 ShortDescription TEXT,
 Description TEXT,
 LanguageId INTEGER,
 FOREIGN KEY(PersonId) REFERENCES Person(PersonId),
 FOREIGN KEY(LanguageId) REFERENCES ResumeLanguage(LanguageId)
 );


-- Resume settings
CREATE TABLE IF NOT EXISTS ResumeSettings
(SettingId INTEGER PRIMARY KEY,
 SettingName TEXT,
 SettingValue TEXT
);
