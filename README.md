# CV Generator - Streamlit App

## Overview
The CV Generator is a Python-based application built with Streamlit, designed to help users create a tailored and professional CV effortlessly. One of its key advantages is the separation of content and formatting, allowing users to focus on their achievements while maintaining a consistent and polished layout.

## Features
- **Content-First Approach**: Users enter their information without worrying about formatting.
- **Headline and Personal Info**: The CV starts with essential details and a brief headline.
- **Project Selection & Sorting**: Users can select their most impactful projects, reorder them, and exclude specific ones as needed.
- **One-Click Generation**: After refining the content, users simply press a button to generate their CV.

## Installation
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

## Usage
1. Open the application in your browser.
2. Enter your personal details and a short headline.
3. Select and sort the projects you want to highlight.
4. Click the **Generate CV** button to create a polished CV.

## Customization
The app allows customization of:
- CV layout and style (modify the template files).

## Contributions
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

