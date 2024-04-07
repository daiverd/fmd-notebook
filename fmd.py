from flask import Flask, request, redirect, render_template, render_template_string 
from tools import convert
from pathlib import Path
from dulwich.repo import Repo
import os, shutil

base_dir = Path(Path(__file__).parent, "markdown")
repo = None

def setup():
    print("Running setup...")
    if not base_dir.exists():
        base_dir.mkdir()
        print(f"Creating {base_dir}")
    if not Path(base_dir, ".git").exists():
        repo = Repo.init(base_dir)
        print(f"Initializing git repo in {base_dir}")
    else:
        repo = Repo(base_dir)
        print(f"Found git repo in {base_dir}")
    if not Path(base_dir, "index.md").exists():
        shutil.copy("templates/index.md", base_dir)
        print("Copied index template")
    print("Setup completed.")

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

@app.errorhandler(404)
def page_not_found(e):
    return '404 bad path!', 404

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
    if not filename.endswith(".md"):
        return redirect(f'/view/{filename}.md')
    content = "File not found." 
    # Construct file path 
    file_path = Path(base_dir, filename)
         # Check if file exists 
    if not is_safe_path(file_path):
        raise file_not_found()
    if file_path.is_file():
        # Read the Markdown file 
        with open(file_path, 'r') as f: 
            markdown_content = f.read() 
            # Convert Markdown to HTML 
            content = convert(markdown_content) 
    else: 
        return redirect(f'/edit/{filename}')
         # Use a simple HTML template and insert the HTML content 
    return render_template("view.html", content=content, filename=filename) 

@app.route('/edit/<path:filename>', methods=['GET', 'POST']) 
def edit_markdown_file(filename): 
    if not filename.endswith(".md"):
        return redirect(f'/edit/{filename}.md')
    content = "File not found." 
    # Construct file path 
    file_path = Path(base_dir, filename)
    if request.method == 'GET':
             # Check if file exists 
        if is_safe_path(file_path) and os.path.isfile(file_path): 
            # Read the Markdown file 
            with open(file_path, 'r') as f: 
                content = f.read() 
        else: 
            content = "# new file" 
             # Use a simple HTML template and insert the HTML content 
        return render_template("edit.html", content=content, filename=filename) 
    else:
        content = request.form.get("text")
        with open(file_path, 'w') as f:
            f.write(content)
        return redirect(f'/view/{filename}')

if __name__ == '__main__': 
    setup()
    app.run(debug=True)
