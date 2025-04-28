import os
import openai
from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
dreams = db["dreams"]
users = db["users"]

openai.api_key = os.getenv("OPENAI_API_KEY")


def interpret_dream(username, message):
    import traceback
    try:
        user = users.find_one({"username": username}) or {}
        history = user.get("history", [])
    except Exception as e:
        print("MongoDB error loading history:", e)
        traceback.print_exc()
        history = []

    system_prompt = {
        "role": "system",
        "content": (
            "You are a dream interpreter with deep knowledge of astrology, symbolism, "
            "and human psychology. Each time the user submits a dream, you should "
            "provide a concise, actionable interpretation of that dream."
        )
    }

    messages = [system_prompt] + history + [{"role": "user", "content": message}]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        interpretation = response.choices[0].message.content

        new_turns = [
            {"role": "user",      "content": message},
            {"role": "assistant", "content": interpretation}
        ]
        users.update_one(
            {"username": username},
            {
                "$push": {
                    "history": {"$each": new_turns},
                    "dreams": {
                        "text": message,
                        "analysis": interpretation
                    }
                }
            }
        )

        return interpretation

    except Exception as e:
        print("OpenAI API failed:", e)
        traceback.print_exc()
        return str(e)
