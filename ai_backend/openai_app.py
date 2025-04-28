from flask import Flask, request, jsonify
import openai
import os

import chat_functions

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json()
    dream = data.get("dream")
    username = data.get("username")

    if not dream:
        return jsonify({"error": "No dream provided"}), 400

    try:
        interpretation = chat_functions.interpret_dream(username, dream)
        return jsonify({"interpretation": interpretation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/glance", methods=["POST"])
def glance():
    data = request.get_json()
    username = data.get("username")

    try:
        glance = chat_functions.get_dream_glance(username)
        return jsonify({"dream_glance": glance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
