from flask import Flask, request, render_template, render_template_string 
from pathlib import Path
import markdown 
import os 

base_dir = Path(Path(__file__).parent, "markdown_files")

app = Flask(__name__) 

# Function to get the list of markdown files 
def get_markdown_files(directory=""):
  """
  Retrieves a glob object containing markdown files from the specified directory using pathlib.
  """

  dir_path = Path(base_dir, directory)

  # Handle potential errors during path construction
  if not is_safe_path(dir_path):
    raise ValueError(str(dir_path))

  if not dir_path.is_absolute():
    raise ValueError("Directory path must be absolute")

  # Use path.glob to find all '.md' files (returns a generator)
  return [path.relative_to(base_dir) for path in dir_path.glob("*.md")]

def is_safe_path(path):
  """
  Checks if a path is within the specified base directory using pathlib.
  """

  path_obj = Path(path)

  # Handle potential errors during path construction
  if not base_dir.is_absolute():
    raise ValueError("Base directory path must be absolute")
  if not path_obj.is_absolute():
    raise ValueError("Input path must be absolute")

  # Check if the resolved path is within the base directory
  return path_obj == base_dir or path_obj.is_relative_to(base_dir)

@app.route('/') 
def index(): 
    files = get_markdown_files() 
    links = '' 
    for file in files: 
        # Create a link for each file 
        links += f'<li><a href="/view/{file}">{file}</a></li>' 
             # Render an HTML list of links
    return f"""<html>                 <head><title>Markdown Files</title></head>                 <body>                     <h1>Available Markdown Files</h1>                     <ul>{links}</ul>                 </body>                </html>""" 

@app.route('/view/<path:filename>') 
def view_markdown_file(filename): 
    content = "File not found." 
    # Construct file path 
    file_path = Path(base_dir, filename)
         # Check if file exists 
    if is_safe_path(file_path) and os.path.isfile(file_path): 
        # Read the Markdown file 
        with open(file_path, 'r') as f: 
            markdown_content = f.read() 
            # Convert Markdown to HTML 
            content = markdown.markdown(markdown_content) 
    else: 
        content = "Markdown file not found!" 
         # Use a simple HTML template and insert the HTML content 
    return render_template("view.html", content=content, filename=filename) 

@app.route('/edit/<path:filename>') 
def edit_markdown_file(filename): 
    content = "File not found." 
    # Construct file path 
    file_path = Path(base_dir, filename)
         # Check if file exists 
    if is_safe_path(file_path) and os.path.isfile(file_path): 
        # Read the Markdown file 
        with open(file_path, 'r') as f: 
            content = f.read() 
    else: 
        content = "# new file" 
         # Use a simple HTML template and insert the HTML content 
    return render_template("edit.html", content=content, filename=filename) 

if __name__ == '__main__': 
    app.run(debug=True)
