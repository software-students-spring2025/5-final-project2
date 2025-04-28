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
    try:
        user = users.find_one({"username": username})
        history = user["history"]

    except:
        history = []

    if not history:
        history = [
            {
                "role": "user",
                "content": """You are a dream interpreter with deep knowledge of astrology, symbolism, and human 
                       psychology. Based on your knowledge and the user's previous dreams, if they have told you about any, you will
                       help the user interpret their dreams and provide them with advice and guidance regarding what their dreams
                       could be telling them about their lives.""",
            }
        ]

    history.append({"role": "user", "content": message})

    response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=history)

    interpretation = response.choices[0].message.content

    history.append({"role": "assistant", "content": interpretation})

    users.update_one({"username": username}, {"$set": {"history": history}})

    dreams.insert_one({"username": username, "dream": message})

    return interpretation
