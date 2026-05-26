from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)

import sqlite3
import bcrypt
import re

app = Flask(__name__)

app.secret_key = "super_secure_secret_key"

# =========================================
# DATABASE INITIALIZATION
# =========================================

def initialize_database():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password BLOB NOT NULL

        )

    """)

    conn.commit()

    conn.close()

initialize_database()

# =========================================
# PASSWORD VALIDATION
# =========================================

def validate_password(password):

    if len(password) < 8:
        return "Password must contain at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return "Password must contain an uppercase letter"

    if not re.search(r"[0-9]", password):
        return "Password must contain a number"

    if not re.search(r"[!@#$%^&*]", password):
        return "Password must contain a special character"

    return None

# =========================================
# HOME
# =========================================

@app.route("/")

def home():

    return redirect(url_for("login"))

# =========================================
# REGISTER ROUTE
# =========================================

@app.route("/register", methods=["GET", "POST"])

def register():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        validation_error = validate_password(password)

        if validation_error:

            flash(validation_error)

            return redirect(url_for("register"))

        hashed_password = bcrypt.hashpw(

            password.encode("utf-8"),

            bcrypt.gensalt()

        )

        try:

            conn = sqlite3.connect("database.db")

            cursor = conn.cursor()

            cursor.execute(

                "INSERT INTO users (username, password) VALUES (?, ?)",

                (username, hashed_password)

            )

            conn.commit()

            flash("Registration Successful")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("Username already exists")

            return redirect(url_for("register"))

        finally:

            conn.close()

    return render_template("register.html")

# =========================================
# LOGIN ROUTE
# =========================================

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute(

            "SELECT * FROM users WHERE username = ?",

            (username,)

        )

        user = cursor.fetchone()

        conn.close()

        if user:

            stored_password = user[2]

            if bcrypt.checkpw(

                password.encode("utf-8"),

                stored_password

            ):

                session["user"] = username

                flash("Login Successful")

                return redirect(url_for("dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")

# =========================================
# DASHBOARD
# =========================================

@app.route("/dashboard")

def dashboard():

    if "user" not in session:

        return redirect(url_for("login"))

    return render_template(

        "dashboard.html",

        username=session["user"]

    )

# =========================================
# LOGOUT
# =========================================

@app.route("/logout")

def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect(url_for("login"))

# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(debug=True)