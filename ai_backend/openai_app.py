from flask import Flask, request, jsonify
import os
from pymongo import MongoClient
import chat_functions

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
users = db["users"]

@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json()
    dream = data.get("dream")
    username = data.get("username", "").strip().lower()
    print("INTERPRET endpoint hit with:", data)

    if not dream:
        return jsonify({"error": "No dream provided"}), 400

    try:
        interpretation = chat_functions.interpret_dream(username, dream)
        return jsonify({"interpretation": interpretation})
    except Exception as e:
        print("Error in /interpret route:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/dream_glance", methods=["GET"])
def dream_glance():
    username = request.args.get("username", "").strip().lower()

    if not username:
        return jsonify({"summary": "No username provided."}), 400

    try:
        user = users.find_one({"username": username}) or {}
        dreams = user.get("dreams", [])

        if not dreams:
            return jsonify({"summary": "No dreams found yet."})

        summary = chat_functions.get_dream_glance(dreams)
        return jsonify({"summary": summary})
    except Exception as e:
        print("Error in /dream_glance route:", e)
        return jsonify({"summary": f"Error generating summary: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)