import requests

from config import GROCY_URL, GROCY_API_KEY


# ============================================================
# Grocy HTTP helpers
# ============================================================

def grocy_headers():
    return {
        "GROCY-API-KEY": GROCY_API_KEY,
        "Content-Type": "application/json",
    }


def grocy_get(endpoint):
    response = requests.get(
        GROCY_URL + endpoint,
        headers=grocy_headers(),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def grocy_post(endpoint, body=None):
    response = requests.post(
        GROCY_URL + endpoint,
        headers=grocy_headers(),
        json=body or {},
        timeout=30,
    )

    response.raise_for_status()

    return response.json()