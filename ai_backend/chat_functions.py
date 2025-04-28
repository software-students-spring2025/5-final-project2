import os
import openai
from pymongo import MongoClient
from datetime import datetime

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
            "provide a concise, actionable interpretation of that dream. Feel free to use the user's previous dreams to interpret the new one. "
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
                        "analysis": interpretation,
                        "date": datetime.utcnow()
                    }
                }
            }
        )

        return interpretation

    except Exception as e:
        print("OpenAI API failed:", e)
        traceback.print_exc()
        return str(e)

def get_dream_glance(username):
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
            "and human psychology. Using all of the dreams available in your conversation with the user, give a summary of "
            "the recurring symbols and feelings in their dreams and give some guidance regarding what it could mean in the life. "
            "Prioritize more recent dreams in your analysis and if there has been a dramatic shift in dream patterns over time, "
            "acknowledge that and note the user's growth or change. "
        )
    }

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages= [system_prompt] + history
        )
        interpretation = response.choices[0].message.content

        return interpretation

    except Exception as e:
        print("OpenAI API failed:", e)
        traceback.print_exc()
        return str(e)