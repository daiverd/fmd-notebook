"""Flask Markdown Notebook: render and edit notes under ``markdown/``,
auto-committing each save to a self-contained dulwich repo."""

import secrets
import shutil
from datetime import date, timedelta
from pathlib import Path

from dulwich import porcelain
from dulwich.repo import Repo
from flask import Flask, abort, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import safe_join

from tools import convert

base_dir = Path(Path(__file__).parent, "markdown")
repo = None

def setup() -> None:
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

def safe_file_path(filename: str) -> Path | None:
    """Join filename under base_dir, returning None if the result would escape."""
    joined = safe_join(str(base_dir), filename)
    return Path(joined) if joined is not None else None

def get_markdown_files(directory: str = "") -> list[str]:
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

def _date_stem(d: date) -> str:
    return d.isoformat()

def _week_stem(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"

_SHORTCUTS = {
    "yesterday": lambda: _date_stem(date.today() - timedelta(days=1)),
    "today":     lambda: _date_stem(date.today()),
    "tomorrow":  lambda: _date_stem(date.today() + timedelta(days=1)),
    "last_week": lambda: _week_stem(date.today() - timedelta(weeks=1)),
    "this_week": lambda: _week_stem(date.today()),
    "next_week": lambda: _week_stem(date.today() + timedelta(weeks=1)),
}

_SHORTCUT_RULE = "<any(yesterday,today,tomorrow,last_week,this_week,next_week):shortcut>"

@app.route(f"/view/{_SHORTCUT_RULE}")
@app.route(f"/view/{_SHORTCUT_RULE}.md")
@app.route(f"/view/<path:project>/{_SHORTCUT_RULE}")
@app.route(f"/view/<path:project>/{_SHORTCUT_RULE}.md")
def view_date_shortcut(shortcut, project=None):
    stem = _SHORTCUTS[shortcut]()
    filename = f"{project}/{stem}" if project else stem
    if safe_file_path(filename + ".md") is None:
        abort(404)
    return redirect(url_for("view_markdown_file", filename=filename))

if __name__ == '__main__':
    app.run(debug=False)
