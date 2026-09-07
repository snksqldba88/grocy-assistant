import threading
import json
import requests
import time
from flask import Flask, request, jsonify, render_template

from config import (
    GROCY_URL,
    NTFY_URL,
    NTFY_INPUT_TOPIC,
    NTFY_RESPONSE_TOPIC,
    NTFY_USER,
    NTFY_PASSWORD,
)


from grocy.products import get_products

from assistant.engine import (
    process_message as assistant_process_message,
)

app = Flask(__name__)

# ============================================================
# Web Chat API
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({
                "response": "Please enter a message."
            }), 400

        print(f"Web chat: {message}")

        result = assistant_process_message(message)

        return jsonify({
            "response": result
        })

    except Exception as e:
        print(f"Web chat error: {e}")

        return jsonify({
            "response": f"❌ Error: {e}"
        }), 500

# ============================================================
# HTTP helpers
# ============================================================


def ntfy_auth():
    if NTFY_USER and NTFY_PASSWORD:
        return NTFY_USER, NTFY_PASSWORD

    return None


def notify(message):
    """
    Send response to grocy-response.
    The assistant does NOT subscribe to this topic.
    """

    response = requests.post(
        f"{NTFY_URL}/{NTFY_RESPONSE_TOPIC}",
        data=message.encode("utf-8"),
        auth=ntfy_auth(),
        headers={
            "Title": "Grocy Assistant",
            "Content-Type": "text/plain; charset=utf-8",
        },
        timeout=30,
    )

    response.raise_for_status()

# ============================================================
# ntfy listener
# ============================================================

def listen_for_messages():
    """
    Listen ONLY to grocy-input.

    Responses are sent to grocy-response,
    so the assistant never receives its own responses.
    """

    subscribe_url = (
        f"{NTFY_URL}/"
        f"{NTFY_INPUT_TOPIC}/json"
    )

    while True:
        try:
            print("Connecting to ntfy...")
            print(subscribe_url)

            with requests.get(
                subscribe_url,
                auth=ntfy_auth(),
                stream=True,
                timeout=(30, None),
            ) as response:

                response.raise_for_status()

                print("Connected to ntfy.")
                print("Waiting for ntfy messages...")
                print()

                for line in response.iter_lines(
                    decode_unicode=True
                ):
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # ntfy sends open/keepalive/message events.
                    if event.get("event") != "message":
                        continue

                    message = event.get("message", "").strip()

                    if not message:
                        continue

                    yield message

        except Exception as e:
            print(
                f"ntfy connection error: {e}"
            )

            print(
                "Retrying in 5 seconds..."
            )

            time.sleep(5)


# ============================================================
# Main processing
# ============================================================
def process_ntfy_message(message):
    print(f"Received: {message}")

    try:
        result = assistant_process_message(message)

        print(result)
        print()

        notify(result)

    except Exception as e:
        print(f"ntfy processing error: {e}")

        try:
            notify(f"❌ Error: {e}")
        except Exception as notify_error:
            print(f"ntfy response error: {notify_error}")


def ntfy_worker():
    for message in listen_for_messages():
        process_ntfy_message(message)

# ============================================================
# Application startup
# ============================================================

def main():
    print("========================================")
    print("       Grocy Web Chat")
    print("========================================")
    print(f"Grocy: {GROCY_URL}")
    print()

    try:
        products = get_products()

        print(
            f"Grocy products: {len(products)}"
        )

    except Exception as e:
        print(
            f"ERROR: Could not connect to Grocy: {e}"
        )
        return

    print("Starting ntfy listener...")
    threading.Thread(
        target=ntfy_worker,
        daemon=True
    ).start()

    print("Starting web server...")
    print("Listening on 0.0.0.0:8080")
    print()

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )


if __name__ == "__main__":
    main()
