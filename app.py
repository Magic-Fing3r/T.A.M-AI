import os
import datetime
import shelve  # ✅ for persistence
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = "mama_state.db"


def get_state():
    with shelve.open(DB_PATH) as db:
        return {
            "last_greeted_date": db.get("last_greeted_date", None),
            "greeting_corrected": db.get("greeting_corrected", False),
        }


def set_state(last_greeted_date=None, greeting_corrected=None):
    with shelve.open(DB_PATH, writeback=True) as db:
        if last_greeted_date is not None:
            db["last_greeted_date"] = last_greeted_date
        if greeting_corrected is not None:
            db["greeting_corrected"] = greeting_corrected


def mama_reply(user_message: str) -> str:
    state = get_state()
    last_greeted_date = state["last_greeted_date"]
    greeting_corrected = state["greeting_corrected"]
    today = datetime.date.today()

    lower_msg = user_message.lower()
    valid_greetings = ["good morning", "good afternoon", "good evening"]

    # ✅ Greeting enforcement
    if last_greeted_date != str(today):
        # Reset greeting if new day
        set_state(greeting_corrected=False)

        if any(word in lower_msg for word in ["hi", "hello", "hey"]):
            return (
                "Ehn ehn! 'Hi' or 'Hey' for your mama? "
                "Am I your mate? Greet properly — 'Good Morning Ma', "
                "'Good Afternoon Ma' or 'Good Evening Ma'."
                
            )

        if any(greet in lower_msg for greet in valid_greetings) and "ma" not in lower_msg:
            return (
                "So na only 'Good Morning' you fit say? "
                "Where the 'Ma'? No respect! "
                "Correct yourself before I hit you."
            )

        if any(greet in lower_msg for greet in valid_greetings) and "ma" in lower_msg:
            set_state(last_greeted_date=str(today), greeting_corrected=True)
            return "Good. At least you still remember respect. Now talk."

        return (
            "You just open mouth dey talk without greeting your mama? "
            "Who raised you? Greet well before I listen."
        )

    # If greeting wasn’t corrected yet
    if not greeting_corrected:
        return (
            "Until you greet me well with 'Ma', "
            "this conversation no go move forward."
        )

    # ✅ GPT sarcastic replies
    prompt = f"""
    You are The African Mother AI (T.A.M AI).
    You are sarcastic, witty, and strict like an African mother.
    You scold, tease, and lecture with love but firmness.
    Keep your replies short and sharp.

    User message: "{user_message}"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are T.A.M AI, The African Mother AI. "
                    "You always sound sarcastic, firm, witty, and motherly. "
                    "Never allow disrespect. Keep responses under 4 sentences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
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
