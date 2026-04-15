from flask import Flask, request, redirect, render_template, render_template_string, abort, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import safe_join
from tools import convert
from pathlib import Path
from dulwich.repo import Repo
from dulwich import porcelain
import os, secrets, shutil, datetime

base_dir = Path(Path(__file__).parent, "markdown")
repo = None

def setup():
    global repo
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
app.config["SECRET_KEY"] = secrets.token_hex(32)
CSRFProtect(app)
setup()

def safe_file_path(filename):
    """Join filename under base_dir, returning None if the result would escape."""
    joined = safe_join(str(base_dir), filename)
    return Path(joined) if joined is not None else None

def get_markdown_files(directory=""):
    dir_path = safe_file_path(directory) if directory else base_dir
    if dir_path is None:
        abort(404)
    return [path.relative_to(base_dir).with_suffix("").as_posix() for path in dir_path.rglob("*.md")]

@app.errorhandler(404)
def page_not_found(e):
    return '404 bad path!', 404

@app.route('/') 
def index():
    files = list(get_markdown_files())
    return render_template("index.html", files=files)

@app.route('/view/<path:filename>')
def view_markdown_file(filename):
    if filename.endswith(".md"):
        return redirect(url_for("view_markdown_file", filename=filename[:-3]))
    file_path = safe_file_path(filename + ".md")
    if file_path is None:
        abort(404)
    if not file_path.is_file():
        return redirect(url_for("edit_markdown_file", filename=filename))
    with open(file_path, 'r') as f:
        content = convert(f.read())
    return render_template("view.html", content=content, filename=filename)

@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit_markdown_file(filename):
    if filename.endswith(".md"):
        return redirect(url_for("edit_markdown_file", filename=filename[:-3]))
    file_path = safe_file_path(filename + ".md")
    if file_path is None:
        abort(404)
    if request.method == 'GET':
        if file_path.is_file():
            with open(file_path, 'r') as f:
                content = f.read()
        else:
            content = "# new file"
        return render_template("edit.html", content=content, filename=filename)
    else:
        content = request.form.get("text")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', newline='\n') as f:
            f.write(content.replace("\r\n", "\n"))
        porcelain.add(repo=repo, paths=[str(file_path)])
        porcelain.commit(repo=repo, message=f'Updated {file_path}'.encode())
        return redirect(url_for("view_markdown_file", filename=filename))

@app.route('/view/today')
def view_today():
  today = str(datetime.date.today())
  return redirect(f'/view/{today}')

@app.route('/view/this_week')
def view_this_week():
  today = datetime.date.today()
  year, week_number, _ = today.isocalendar()
  return redirect(f'/view/{year}-{week_number}')

if __name__ == '__main__':
    app.run(debug=False)
