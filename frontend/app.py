from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, url_for
import requests
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret")

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
users = db["users"]
dreams = db["dreams"]

AI_SERVICE_URL = "http://ai_backend:6000/interpret"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form["password2"]
        
        if users.find_one({"username": username}):
            return render_template("register.html", error="Username already exists.")

        if password != password2:
            return render_template("register.html", error="Passwords do not match.")

        hashed_pw = generate_password_hash(password)
        users.insert_one({"username": username, "password": hashed_pw})
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))

        return render_template("login.html", error="Inavlid credentials.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users.find_one({"username": username}) or {}
    dream_entries = user.get("dreams", [])

    dream_dates = sorted({
        entry.get("date").date() for entry in dream_entries if "date" in entry
    }, reverse=True)

    streak = 0
    today = datetime.utcnow().date()

    for i, day in enumerate(dream_dates):
        expected_day = today - timedelta(days=i)
        if day == expected_day:
            streak += 1
        else:
            break


    return render_template('index.html', username=username, streak=streak)

@app.route('/analyze', methods=['GET','POST'])
def analyze():
    if 'username' not in session:
        return redirect(url_for('login'))

    interpretation = None
    error = None
    previous = ""

    if request.method == "POST":
        previous = request.form.get('dream', '').strip()
        if not previous:
            error = "Please enter a dream."
        else:
            try:
                res = requests.post(
                    AI_SERVICE_URL,
                    json={"dream": previous, "username": session['username']}
                )
                data = res.json()
                interpretation = (
                    data.get("interpretation")
                    or data.get("error")
                    or "No interpretation found."
                )
            except Exception as e:
                error = f"Error: {e}"

    return render_template(
        'analyze.html',
        previous=previous,
        interpretation=interpretation,
        error=error
    )




@app.route('/entries')
def entries():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_dreams = dreams.find({"username": username})

    return render_template('entries.html', dreams=user_dreams, username=username)


@app.route('/export')
def export():
    return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  
