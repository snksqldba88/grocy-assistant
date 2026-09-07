from notifications.ntfy import (
    notify,
    listen_for_messages,
)


print("Testing ntfy connection...")

messages = listen_for_messages()

print("Waiting for a message...")

message = next(messages)

print(f"Received: {message}")

notify(f"Test response: received '{message}'")

print("Response sent successfully.")