import os
import datetime
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Track greetings per day
last_greeted_date = None

def mama_reply(user_message):
    global last_greeted_date
    today = datetime.date.today()

    greeted_today = (last_greeted_date == today)

    # Greeting enforcement
    if not greeted_today and any(
        word in user_message.lower()
        for word in ["hi", "hello", "good morning", "good afternoon", "good evening"]
    ):
        last_greeted_date = today
        return "Ehen! At least you sabi greet today. No make me para."

    if not greeted_today:
        return "So you just waka enter here like oga? You no fit greet? Try am again and I go find my slipper."

    # Small pool of random African mum threats for spice
    threats = [
        "I go use slipper reset your brain.",
        "Better respect yourself before I knack you wooden spoon.",
        "You dey craze? I fit drag your ear now-now.",
        "Keep am up, na koboko go end this your nonsense."
    ]
    random_threat = random.choice(threats)

    # GPT-powered sarcastic African mother reply
    prompt = f"""
You are The African Mother AI (T.A.M AI). 
You reply in Nigerian Pidgin mixed with African mother sarcasm and stern tone.
You are witty, short, and scolding, not playful. 
Sometimes, insert one of these threats naturally: {random_threat}.
Keep reply maximum 2–4 sentences, never long speeches. Always sound like a real African mum correcting her child.

User message: "{user_message}"
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are T.A.M AI, The African Mother AI. You are sarcastic, stern, witty, and scolding. Replies are short and sharp in Nigerian Pidgin."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=160,
        temperature=0.95,
        top_p=0.9,
    )

    return response.choices[0].message["content"].strip()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    reply = mama_reply(user_message)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
