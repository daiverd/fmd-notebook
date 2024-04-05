from flask import Flask, render_template_string 
from pathlib import Path
import markdown 
import os 

base_dir = Path(Path(__file__).parent, "markdown_files")

app = Flask(__name__) 

# Function to get the list of markdown files 
def get_markdown_files(): 
    md_files = [f for f in os.listdir("markdown_files") if f.endswith('.md')] 
    return md_files 

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
  return path_obj.is_relative_to(base_dir)

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
    template = """ 
    <!DOCTYPE html>     <html>     <head>         <title>Markdown Viewer</title>     </head> 
    <body>         {{ content | safe }}     </body>     </html>     """ 
    return render_template_string(template, content=content) 

if __name__ == '__main__': 
    app.run(debug=True)
