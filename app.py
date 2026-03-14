from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from health_agent import analyze_health
from chart import generate_health_chart
import pandas as pd
from flask_login import current_user
import sqlite3


def init_db():
    conn = sqlite3.connect("vitalai.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        health_score INTEGER
    )
    """)

    conn.commit()
    conn.close()
    

init_db()
app = Flask(__name__)
app.secret_key = "vitalai_secret"

# ---------------- LOGIN MANAGER ---------------- #

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Simple user storage (for project demo)
users = {
    "admin": {"password": "1234"}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ---------------- HOME PAGE ---------------- #

@app.route("/")
def home():
    return render_template("home.html")

# ---------------- LOGIN PAGE ---------------- #

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("vitalai.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            login_user(User(username))
            return redirect(url_for("assistant"))

        else:
            return "Invalid login"

    return render_template("login.html")

# ---------------- SIGNUP PAGE ---------------- #

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("vitalai.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# ---------------- AI ASSISTANT ---------------- #

@app.route("/assistant")
@login_required
def assistant():
    return render_template("index.html")

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
@login_required
def dashboard():

    conn = sqlite3.connect("vitalai.db")

    df = pd.read_sql_query(
        "SELECT health_score FROM health_logs WHERE user_id=?",
        conn,
        params=(current_user.id,)
    )

    conn.close()

    # If no data exists
    if df.empty:
        latest_score = 0
        avg_score = 0
        total_entries = 0
        best_score = 0
        worst_score = 0
        risk_label = "No Data"
        risk_class = "gray"

    else:
        latest_score = df["health_score"].iloc[-1]
        avg_score = round(df["health_score"].mean(),1)
        total_entries = len(df)

        best_score = df["health_score"].max()
        worst_score = df["health_score"].min()

        if latest_score >= 80:
            risk_label = "Healthy"
            risk_class = "green"
        elif latest_score >= 60:
            risk_label = "Moderate"
            risk_class = "orange"
        else:
            risk_label = "Risk"
            risk_class = "red"

    generate_health_chart(current_user.id)

    return render_template(
        "dashboard.html",
        latest_score=latest_score,
        avg_score=avg_score,
        total_entries=total_entries,
        best_score=best_score,
        worst_score=worst_score,
        risk_label=risk_label,
        risk_class=risk_class
    )

# ---------------- HEALTH ANALYSIS API ---------------- #

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():

    data = request.json
    email = data.get("email")
    result = analyze_health(data, email)

    conn = sqlite3.connect("vitalai.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO health_logs (user_id, health_score) VALUES (?, ?)",
        (current_user.id, result["health_score"])
    )

    conn.commit()
    conn.close()

    return jsonify(result)

# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)