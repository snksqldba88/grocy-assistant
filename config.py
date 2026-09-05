import os
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

load_dotenv()

GROCY_URL = os.environ["GROCY_URL"].rstrip("/")
GROCY_API_KEY = os.environ["GROCY_API_KEY"]

NTFY_URL = os.environ.get(
    "NTFY_URL",
    "http://ntfy"
).rstrip("/")

NTFY_INPUT_TOPIC = os.environ.get(
    "NTFY_INPUT_TOPIC",
    "grocy-input"
)

NTFY_RESPONSE_TOPIC = os.environ.get(
    "NTFY_RESPONSE_TOPIC",
    "grocy-response"
)

NTFY_USER = os.environ.get("NTFY_USER")
NTFY_PASSWORD = os.environ.get("NTFY_PASSWORD")