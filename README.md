# CV Generator - Streamlit App

## Overview
The CV Generator is a Python-based application built with Streamlit, designed to help users create a tailored and professional CV effortlessly. One of its key advantages is the separation of content and formatting, allowing users to focus on their achievements while maintaining a consistent and polished layout.

## Features
- **Content-First Approach**: Users enter their information without worrying about formatting.
- **Headline and Personal Info**: The CV starts with essential details and a brief headline.
- **Project Selection & Sorting**: Users can select their most impactful projects, reorder them, and exclude specific ones as needed.
- **One-Click Generation**: After refining the content, users simply press a button to generate their CV.

## Installation - local installation
To run the CV Generator locally, follow these steps:

1. Clone this repository:
   ```sh
   git clone https://github.com/Marcel-Jan/cvgen-sqlite.git
   cd cv-generator
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   streamlit run app.py
   ```

## Installation - Docker container
cvgen-sqlite is available as Docker image: [https://hub.docker.com/r/marceljan/cvgen-sqlite]
To run cvgen-sqlite as Docker container:
1. Install Docker Desktop: [https://www.docker.com/products/docker-desktop/]

2. Start a cvgen-sqlite Docker container:
   ```sh
   docker run -d -p 8501:8501 --name cvgen-sqlite --platform linux/amd64 -d cvgen-sqlite
   ```

3. Go to the app in your browser: [https://localhost:8501]


## Usage
1. Open the application in your browser.
2. Go to the StartHere page and enter your personal details.
3. On the Headline page enter the headline of your resume.
4. Enter the projects you want to highlight.
5. Enter work experience, education, certification and other details.
6. Go to the Generate page, order your top projects. And click the **Generate Resume** button to create a polished CV. Then download it as PDF format.

## Customization
The app allows customization of:
- CV layout and style (modify the template files).

## Contributions
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

