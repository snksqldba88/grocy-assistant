import threading

from flask import Flask, request, jsonify, render_template

from config.config import (
    GROCY_URL,
)

from notifications.ntfy import (
    notify,
    listen_for_messages,
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
