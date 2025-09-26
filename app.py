import os
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Track greetings per day
last_greeted_date = None


def mama_reply(user_message: str) -> str:
    """
    Mama's reply engine:
    - If no greeting for the day → Mama vex first.
    - Otherwise → sarcastic + witty + African mother energy.
    """
    global last_greeted_date
    today = datetime.date.today()
    greeted_today = (last_greeted_date == today)

    greetings = ["hi", "hello", "good morning", "good afternoon", "good evening"]

    # First check greeting
    if not greeted_today and any(word in user_message.lower() for word in greetings):
        last_greeted_date = today
        return "Ah, now you sabi greet. Na so e suppose be. At least you still get small home training."

    if not greeted_today:
        return (
            "So you just waka enter without greeting your mama? "
            "No be juju be that? Abeg, start again with correct greeting."
        )

    # Mama's sarcasm via GPT
    prompt = f"""
You are The African Mother AI (T.A.M AI).
Your voice = sarcastic, witty, full of African mother sass + Pidgin English.
Reply short (2–3 sentences max). 
Mix Nigerian Pidgin + African mother energy. 
User: "{user_message}"
Mama:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are T.A.M AI, The African Mother AI. Always sarcastic, sassy, and motherly. Speak in Nigerian Pidgin mixed with African mum tone.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.9,
    )

    return response.choices[0].message.content.strip()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    reply = mama_reply(user_message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
