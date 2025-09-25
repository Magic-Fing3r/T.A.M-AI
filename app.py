import os
import random
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load proverbs from file
with open(os.path.join(os.path.dirname(__file__), "../data/proverbs.txt"), "r", encoding="utf-8") as f:
    proverbs = [line.strip() for line in f if line.strip()]

# Track greetings per day
last_greeted_date = None

def mama_reply(user_message):
    global last_greeted_date

    today = datetime.date.today()

    # Check if greeted today
    greeted_today = (last_greeted_date == today)

    if not greeted_today and any(word in user_message.lower() for word in ["hi", "hello", "good morning", "good afternoon", "good evening"]):
        last_greeted_date = today
        return "Ah, now you sabi greet. At least you no forget yourself today."

    if not greeted_today:
        return "So you just waka come here without greeting your mama? In my house? No respect at all o!"

    # Use GPT to generate sarcastic response
    prompt = f"""
You are The African Mother AI (T.A.M AI). You always reply with sarcasm, wit, and African mother energy.
User message: "{user_message}"
Reply in Nigerian Pidgin English mixed with African motherly tone.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are T.A.M AI, The African Mother AI. You always sound sarcastic and motherly."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.9,
    )

    return response.choices[0].message["content"].strip()


@app.route("/proverb", methods=["GET"])
def get_proverb():
    return jsonify({"proverb": random.choice(proverbs)})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    reply = mama_reply(user_message)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
