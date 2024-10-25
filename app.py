from flask import Flask, request, session, render_template, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from config import db_config

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "super_secret_key"
Session(app)


def get_db_connection():
    return mysql.connector.connect(**db_config)


# Registration Routes
@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        data = request.form
        hashed_password = generate_password_hash(data["password"])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)",
                       (data["name"], data["email"], hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register_student.html")


@app.route("/register_mentor", methods=["GET", "POST"])
def register_mentor():
    if request.method == "POST":
        data = request.form
        hashed_password = generate_password_hash(data["password"])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mentors (name, email, password) VALUES (%s, %s, %s)",
                       (data["name"], data["email"], hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register_mentor.html")


# Unified Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        user_type = data["user_type"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check login based on user type
        if user_type == "student":
            cursor.execute("SELECT * FROM students WHERE email = %s", (data["email"],))
        elif user_type == "mentor":
            cursor.execute("SELECT * FROM mentors WHERE email = %s", (data["email"],))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # Authenticate user
        if user and check_password_hash(user["password"], data["password"]):
            session[f"{user_type}_id"] = user["id"]
            return redirect(url_for(f"dashboard_{user_type}"))
        else:
            return "Invalid credentials, please try again.", 401

    return render_template("login.html")


@app.route("/dashboard_student")
def dashboard_student():
    if "student_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard_student.html")


@app.route("/dashboard_mentor")
def dashboard_mentor():
    if "mentor_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard_mentor.html")


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    session.pop("mentor_id", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
