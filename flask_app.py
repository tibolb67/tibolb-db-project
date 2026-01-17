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


from flask import session, flash

def _get_user_accounts():
    return db_read(
        "SELECT account_id, name, type FROM accounts WHERE user_id=%s ORDER BY account_id",
        (current_user.id,),
    )

def _get_categories():
    return db_read("SELECT kategorie_id, name FROM kategorien ORDER BY name")

def _selected_account_id(accounts):
    sel = session.get("selected_account_id")
    if sel and any(a["account_id"] == int(sel) for a in accounts):
        return int(sel)
    if accounts:
        session["selected_account_id"] = int(accounts[0]["account_id"])
        return int(accounts[0]["account_id"])
    return None


@app.route("/tracker", methods=["GET", "POST"])
@login_required
def tracker():
    accounts = _get_user_accounts()
    categories = _get_categories()
    selected = _selected_account_id(accounts)

    # Handle all actions from this page via "action"
    if request.method == "POST":
        action = request.form.get("action", "")

        # Switch account
        if action == "switch_account":
            new_id = request.form.get("account_id")
            ok = db_read(
                "SELECT account_id FROM accounts WHERE user_id=%s AND account_id=%s",
                (current_user.id, new_id),
                single=True,
            )
            if ok:
                session["selected_account_id"] = int(new_id)
            return redirect(url_for("tracker"))

        # Add account
        if action == "add_account":
            name = (request.form.get("name") or "").strip()
            acc_type = request.form.get("type") or "private"
            if not name:
                flash("Account name darf nicht leer sein.", "warning")
                return redirect(url_for("tracker"))

            exists = db_read(
                "SELECT account_id FROM accounts WHERE user_id=%s AND name=%s",
                (current_user.id, name),
                single=True,
            )
            if exists:
                flash("Account existiert schon.", "warning")
                return redirect(url_for("tracker"))

            db_write(
                "INSERT INTO accounts (user_id, name, type) VALUES (%s, %s, %s)",
                (current_user.id, name, acc_type),
            )
            flash("Account erstellt ", "success")
            return redirect(url_for("tracker"))

        # Add category
        if action == "add_category":
            cat_name = (request.form.get("cat_name") or "").strip()
            if not cat_name:
                flash("Kategorie darf nicht leer sein.", "warning")
                return redirect(url_for("tracker"))

            exists = db_read(
                "SELECT kategorie_id FROM kategorien WHERE name=%s",
                (cat_name,),
                single=True,
            )
            if exists:
                flash("Kategorie existiert schon.", "warning")
                return redirect(url_for("tracker"))

            db_write("INSERT INTO kategorien (name) VALUES (%s)", (cat_name,))
            flash("Kategorie erstellt ", "success")
            return redirect(url_for("tracker"))

        # Add expense
        if action == "add_expense":
            if not selected:
                flash("Bitte zuerst einen Account erstellen.", "warning")
                return redirect(url_for("tracker"))

            kategorie_id = request.form.get("kategorie_id")
            betrag = request.form.get("betrag")
            datum = request.form.get("datum")  # datetime-local

            if not (kategorie_id and betrag and datum):
                flash("Bitte alle Felder ausfüllen.", "warning")
                return redirect(url_for("tracker"))

            db_write(
                "INSERT INTO ausgaben (account_id, kategorie_id, datum, betrag) VALUES (%s, %s, %s, %s)",
                (selected, kategorie_id, datum, betrag),
            )
            flash("Ausgabe gespeichert 💸", "success")
            return redirect(url_for("tracker"))

        # Delete expense
        if action == "delete_expense":
            ausgabe_id = request.form.get("ausgabe_id")
            if selected and ausgabe_id:
                db_write(
                    "DELETE FROM ausgaben WHERE ausgabe_id=%s AND account_id=%s",
                    (ausgabe_id, selected),
                )
                flash("Ausgabe gelöscht 🧹", "success")
            return redirect(url_for("tracker"))

    # Load expenses + totals
    expenses = []
    total_month = 0

    if selected:
        expenses = db_read(
            """
            SELECT a.ausgabe_id, a.datum, a.betrag, k.name AS kategorie
            FROM ausgaben a
            JOIN kategorien k ON k.kategorie_id = a.kategorie_id
            WHERE a.account_id=%s
            ORDER BY a.datum DESC
            LIMIT 100
            """,
            (selected,),
        )

        s = db_read(
            """
            SELECT COALESCE(SUM(betrag),0) AS total
            FROM ausgaben
            WHERE account_id=%s
              AND YEAR(datum)=YEAR(CURDATE())
              AND MONTH(datum)=MONTH(CURDATE())
            """,
            (selected,),
            single=True,
        )
        total_month = (s or {}).get("total", 0)

    return render_template(
        "tracker.html",
        accounts=accounts,
        categories=categories,
        selected_account_id=selected,
        expenses=expenses,
        total_month=total_month,
    )


@app.route("/tracker/overview")
@login_required
def tracker_overview():
    # Simple overview: totals per category (current month, selected account)
    accounts = _get_user_accounts()
    selected = _selected_account_id(accounts)

    rows = []
    if selected:
        rows = db_read(
            """
            SELECT k.name AS kategorie, COALESCE(SUM(a.betrag),0) AS total
            FROM ausgaben a
            JOIN kategorien k ON k.kategorie_id=a.kategorie_id
            WHERE a.account_id=%s
              AND YEAR(a.datum)=YEAR(CURDATE())
              AND MONTH(a.datum)=MONTH(CURDATE())
            GROUP BY k.name
            ORDER BY total DESC
            """,
            (selected,),
        )

    return render_template(
        "tracker_overview.html",
        accounts=accounts,
        selected_account_id=selected,
        rows=rows,
    )


if __name__ == "__main__":
    app.run()
