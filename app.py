import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Track daily greetings
last_greeted_date = None


def mama_reply(user_message: str) -> str:
    global last_greeted_date

    today = datetime.now().date()
    disrespectful = False

    # Check if user greeted Mama today
    if "good morning" in user_message.lower() or "good afternoon" in user_message.lower() or "good evening" in user_message.lower():
        last_greeted_date = today
    else:
        if last_greeted_date != today:
            disrespectful = True

    # Mama’s personality
    system_prompt = """
    You are Mama, an elder Nigerian mother powered by T.A.M AI. 
    You always reply in a caring but strict Nigerian tone, full of proverbs, wisdom, and motherly advice.
    """

    if disrespectful:
        system_prompt += (
            "\nThe user has not greeted you today. Scold them about being disrespectful "
            "and remind them that greeting elders is important before giving any advice."
        )

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast and cheap; can switch to gpt-4o
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_message},
        ],
        temperature=0.9,
    )

    return response.choices[0].message.content


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        reply = mama_reply(user_message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
