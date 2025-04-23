from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/interpret', methods=['POST'])
def interpret():
    data = request.get_json()
    dream = data.get("dream")

    if not dream:
        return jsonify({"error": "No dream provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"What does this dream mean? {dream}"}]
        )
        interpretation = response.choices[0].message['content']
        return jsonify({"interpretation": interpretation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
