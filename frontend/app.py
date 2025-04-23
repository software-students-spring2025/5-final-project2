from flask import Flask, render_template, request
import requests
from pymongo import MongoClient
import os

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.dream_journal
dreams_collection = db.dreams

AI_SERVICE_URL = "http://ai_backend:6000/interpret"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    dream_text = request.form['dream']
    dreams_collection.insert_one({"text": dream_text})

    try:
        res = requests.post(AI_SERVICE_URL, json={"dream": dream_text})
        data = res.json()
        interpretation = data.get("interpretation", "No interpretation found.")
    except Exception as e:
        interpretation = f"Error: {e}"

    return render_template('result.html', interpretation=interpretation)

@app.route('/entries')
def entries():
    all_dreams = list(dreams_collection.find())
    return render_template('entries.html', dreams=all_dreams)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  
