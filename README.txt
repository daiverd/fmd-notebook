# Flask Markdown Notebook - README
This Flask application provides a simple web interface for managing Markdown files stored in a Git repository.
Features
* List Markdown Files: View a list of all available Markdown files.
* View Markdown Content: Render and display the content of a specific Markdown file.
* Edit Markdown Files: Edit the content of a Markdown file in a web editor.
* Version Control (Git): Automatically stages and commits changes made to Markdown files.
* Date-based Navigation: Navigate to Markdown files named according to today's date or the current ISO week number
## Setup
1. Install Requirements:
Bash
`pip install -r requirements.txt`
2. Run the Application:
Bash
`python fmd.py`
This will start the Flask development server, usually accessible at http://127.0.0.1:5000/ in your web browser.
## Usage
* View Files: Visit the root URL (/) to see a list of available Markdown files.
* View Content: Click on a file name to view its rendered content.
* Edit Content: Click the "Edit" button on the view page to edit the Markdown content. Save changes to commit them to the Git repository.
## Date-based.md files
You can access files directly using URLs like:
* /view/today: View the Markdown file named after today's date (e.g., 2024-04-07.md).
* /view/this_week: View the Markdown file named after the current ISO week number and year (e.g., 2024-15.md).
