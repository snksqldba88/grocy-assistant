import json
import os
import re
import requests

GROCY_URL = os.environ["GROCY_URL"].rstrip("/")
GROCY_API_KEY = os.environ["GROCY_API_KEY"]

NTFY_URL = os.environ.get("NTFY_URL", "http://ntfy").rstrip("/")
NTFY_INPUT_TOPIC = os.environ["NTFY_INPUT_TOPIC"]
NTFY_RESPONSE_TOPIC = os.environ["NTFY_RESPONSE_TOPIC"]
NTFY_USER = os.environ["NTFY_USER"]
NTFY_PASSWORD = os.environ["NTFY_PASSWORD"]

UNIT_ALIASES = {
    "kg": "kilogram",
    "kgs": "kilogram",
    "kilograms": "kilogram",
    "g": "gram",
    "grams": "gram",
    "l": "litre",
    "liter": "litre",
    "liters": "litre",
    "litres": "litre",
    "gal": "gal",
    "gallon": "gal",
    "gallons": "gal",
    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",
    "pc": "piece",
    "pcs": "piece",
    "pieces": "piece",
}

GROCY_HEADERS = {
    "GROCY-API-KEY": GROCY_API_KEY,
    "Content-Type": "application/json",
}


def grocy_get(path):
    response = requests.get(
        f"{GROCY_URL}{path}",
        headers=GROCY_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def grocy_post(path, payload):
    response = requests.post(
        f"{GROCY_URL}{path}",
        headers=GROCY_HEADERS,
        json=payload,
        timeout=30,
    )
    return response


def notify(message):
    response = requests.post(
        f"{NTFY_URL}/{NTFY_RESPONSE_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": "Grocy Assistant",
            "Tags": "shopping_cart",
        },
	auth=(NTFY_USER, NTFY_PASSWORD),
        timeout=30,
    )
    response.raise_for_status()


def load_products():
    products = grocy_get("/api/objects/products")

    return {
        p["name"].strip().lower(): p
        for p in products
        if p.get("active", 1)
    }


def get_unit_name(unit_id):
    units = grocy_get("/api/objects/quantity_units")

    for unit in units:
        if unit["id"] == unit_id:
            return unit["name"].lower()

    return None


def parse_command(message):
    pattern = (
        r"^\s*([+-])\s+"
        r"(.+?)\s+"
        r"([0-9]+(?:\.[0-9]+)?)\s*"
        r"([a-zA-Z]+)\s*$"
    )

    match = re.match(pattern, message)

    if not match:
        return None

    operation = match.group(1)
    product = match.group(2).strip()
    amount = float(match.group(3))
    unit = match.group(4).strip().lower()

    return operation, product, amount, unit


def update_grocy(operation, product_name, amount, unit):
    products = load_products()

    product = products.get(product_name.lower())

    if not product:
        return f"❌ Product not found: {product_name}"

    product_id = product["id"]

    stock_unit_id = product["qu_id_stock"]
    stock_unit = get_unit_name(stock_unit_id)

    if not stock_unit:
        return f"❌ Could not determine stock unit for {product['name']}."

    unit = UNIT_ALIASES.get(unit, unit)
    if unit != stock_unit:
        return (
            f"❌ Unit mismatch for {product['name']}\n\n"
            f"Grocy stock unit: {stock_unit}\n"
            f"You entered: {unit}"
        )

    if operation == "+":
        endpoint = f"/api/stock/products/{product_id}/add"

        payload = {
            "amount": amount,
            "transaction_type": "purchase",
            "price": 0,
            "best_before_date": None,
            "location_id": product["location_id"],
        }

        action = "Added"

    else:
        endpoint = f"/api/stock/products/{product_id}/consume"

        payload = {
            "amount": amount,
            "spoiled": False,
        }

        action = "Consumed"

    response = grocy_post(endpoint, payload)

    if response.status_code not in (200, 201):
        return (
            f"❌ Grocy update failed\n\n"
            f"Product: {product['name']}\n"
            f"HTTP: {response.status_code}\n"
            f"{response.text}"
        )

    try:
        stock = grocy_get(
            f"/api/stock/products/{product_id}"
        )

        new_amount = stock["stock_amount_aggregated"]

        return (
            f"✅ Grocy updated\n\n"
            f"{product['name']}\n"
            f"{action}: {amount:g} {stock_unit}\n"
            f"New stock: {new_amount:g} {stock_unit}"
        )

    except Exception:
        return (
            f"✅ Grocy updated\n\n"
            f"{product['name']}\n"
            f"{action}: {amount:g} {stock_unit}"
        )


def main():
    print("========================================")
    print("       Grocy Assistant")
    print("========================================")
    print(f"Grocy: {GROCY_URL}")
    print(f"ntfy:  {NTFY_URL}")
    print(f"Input topic: {NTFY_INPUT_TOPIC}")
    print(f"Response topic: {NTFY_RESPONSE_TOPIC}")
    print()

    products = load_products()

    print(f"Grocy products: {len(products)}")
    print("Waiting for ntfy messages...")
    print()

    subscribe_url = f"{NTFY_URL}/{NTFY_INPUT_TOPIC}/json"

    with requests.get(
        subscribe_url,
        stream=True,
        timeout=None,
	auth=(NTFY_USER, NTFY_PASSWORD),
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines(
            decode_unicode=True
        ):

            if not line:
                continue

            try:
                event = json.loads(line)

                if event.get("event") != "message":
                    continue

                message = event.get(
                    "message", ""
                ).strip()

                print(f"Received: {message}")

                parsed = parse_command(message)

                if not parsed:
                    notify(
                        "❌ Invalid command.\n\n"
                        "Examples:\n"
                        "+ tomato 2 kg\n"
                        "- eggs 5\n"
                        "+ milk 1 gal"
                    )
                    continue

                operation, product, amount, unit = parsed

                result = update_grocy(
                    operation,
                    product,
                    amount,
                    unit,
                )

                print(result)
                print()

                notify(result)

            except Exception as e:
                print(
                    f"ERROR processing message: {e}"
                )


if __name__ == "__main__":
    main()
