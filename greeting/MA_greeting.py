from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)


def get_greeting():
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good night"


@app.route("/greetAPI", methods=["GET"])
def greet():
    greeting = get_greeting()
    return jsonify({"greeting": greeting})


if __name__ == "__main__":
    app.run(debug=True, port=5003)
