from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read("SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due", (current_user.id,))
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write("INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)", (current_user.id, content, due, ))
    return redirect(url_for("index"))

@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))




@app.route("/dbexplorer", methods=["GET", "POST"])
@login_required
def dbexplorer():
    # 1) Fetch all table names (MySQL)
    tables_raw = db_read("SHOW TABLES")
    all_tables = [next(iter(r.values())) for r in tables_raw]  # first column of each dict

    # 2) Defaults
    selected_tables = []
    limit = 50
    results = {}
    error = None

    # 3) Handle form submit
    if request.method == "POST":
        selected_tables = request.form.getlist("tables")

        # limit parsing + guardrails
        try:
            limit = int(request.form.get("limit", 50))
        except ValueError:
            limit = 50
        limit = max(1, min(limit, 1000))

        # Optional: quick "jump to table" text field
        quick_table = (request.form.get("quick_table") or "").strip()
        if quick_table:
            selected_tables = list(dict.fromkeys(selected_tables + [quick_table]))  # add unique

        allowed = set(all_tables)

        for t in selected_tables:
            if t not in allowed:
                error = f"Unknown table: {t}"
                continue

            # Backticks are important for table names; we still validate against allowed set.
            rows = db_read(f"SELECT * FROM `{t}` LIMIT %s", (limit,))
            results[t] = rows

    return render_template(
        "dbexplorer.html",
        all_tables=all_tables,
        selected_tables=selected_tables,
        results=results,
        limit=limit,
        error=error,
    )


from flask import render_template
from flask_login import login_required

@app.route("/usecases")
@login_required
def usecases_index():
    return render_template("usecases_index.html")

@app.route("/usecase1")
@login_required
def usecase1():
    return render_template("usecase1.html")

@app.route("/usecase2")
@login_required
def usecase2():
    return render_template("usecase2.html")

@app.route("/usecase3")
@login_required
def usecase3():
    return render_template("usecase3.html")

@app.route("/usecase4")
@login_required
def usecase4():
    return render_template("usecase4.html")

@app.route("/usecase5")
@login_required
def usecase5():
    return render_template("usecase5.html")


if __name__ == "__main__":
    app.run()
