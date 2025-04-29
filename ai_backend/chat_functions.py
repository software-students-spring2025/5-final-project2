import openai
import os
from pymongo import MongoClient
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
users = db["users"]

openai.api_key = os.getenv("OPENAI_API_KEY")

def interpret_dream(username, dream_text):
    username = username.strip().lower()

    try:
        system_prompt = {
            "role": "system",
            "content": (
                "You are a dream interpreter with deep knowledge of astrology, symbolism, "
                "and human psychology. Provide a concise, actionable interpretation of the user's dream. "
                "If the user has previously told you about their dreams, feel free to reference any dreams "
                "that you think may relate to the most recent one and expalin how they are connected. "
            ),
        }

        user = users.find_one({"username": username}) or {}
        dreams = user.get("dreams", [])

        prev_dreams = [{"role": "user", "content": dream.get("text", "")} for dream in dreams]

        messages = [system_prompt] + prev_dreams + [{"role": "user", "content": dream_text}]

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        interpretation = response.choices[0].message.content

        update_result = users.update_one(
            {"username": username},
            {
                "$push": {
                    "dreams": {
                        "text": dream_text,
                        "analysis": interpretation,
                        "date": datetime.utcnow()
                    }
                }
            }
        )

        print(f"Update result for {username}: matched={update_result.matched_count}, modified={update_result.modified_count}")

        return interpretation

    except Exception as e:
        print("Error interpreting dream:", e)
        return "Could not interpret dream."
    
def get_dream_glance(dreams):
    if not dreams:
        return "No dream data available."

    analyses = sorted(
        [d.get("analysis", "") for d in dreams if d.get("analysis")],
        key=lambda x: x.lower() != "",  
        reverse=True
    )

    if not analyses:
        return "No dream insights found."

    dream_summary_input = "\n\n".join(analyses[-3:])

    system_prompt = {
        "role": "system",
        "content": (
            "You are a dream analyst. Summarize the recurring themes, emotions, and meanings "
            "across the following dream interpretations. Offer helpful insight and advice."
        ),
    }

    messages = [
        system_prompt,
        {"role": "user", "content": dream_summary_input}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI API error:", e)
        return "Could not generate dream summary."