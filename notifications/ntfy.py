import json
import time

import requests

from config.config import (
    NTFY_URL,
    NTFY_INPUT_TOPIC,
    NTFY_RESPONSE_TOPIC,
    NTFY_USER,
    NTFY_PASSWORD,
)


def ntfy_auth():
    if NTFY_USER and NTFY_PASSWORD:
        return NTFY_USER, NTFY_PASSWORD

    return None


def notify(message):
    """
    Send a response to the Grocy response topic.
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


def listen_for_messages():
    """
    Listen only to the Grocy input topic.

    Messages received from the input topic are yielded
    one at a time to the caller.
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

                    if event.get("event") != "message":
                        continue

                    message = event.get("message", "").strip()

                    if not message:
                        continue

                    yield message

        except Exception as e:
            print(f"ntfy connection error: {e}")
            print("Retrying in 5 seconds...")

            time.sleep(5)