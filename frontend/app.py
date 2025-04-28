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
    return render_template('index.html', username=session['username'])

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'username' not in session:
        return redirect(url_for('login'))

    dream_text = request.form.get('dream', '')
    username = session['username']

    if not dream_text.strip():
        return "Please enter a dream."

    try:
        res = requests.post("http://ai_backend:6000/interpret", json={"dream": dream_text, "username": username})
        data = res.json()
        interpretation = data.get("interpretation", "No interpretation found.")
    except Exception as e:
        interpretation = f"Error: {e}"

    return render_template('result.html', interpretation=interpretation)

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
