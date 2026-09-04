import os
import re
import json
import requests
from flask import Flask, request, jsonify, render_template
from datetime import date, timedelta

# ============================================================
# Configuration
# ============================================================

GROCY_URL = os.environ["GROCY_URL"].rstrip("/")
GROCY_API_KEY = os.environ["GROCY_API_KEY"]

NTFY_URL = os.environ.get("NTFY_URL", "http://ntfy").rstrip("/")
NTFY_INPUT_TOPIC = os.environ.get("NTFY_INPUT_TOPIC", "grocy-input")
NTFY_RESPONSE_TOPIC = os.environ.get("NTFY_RESPONSE_TOPIC", "grocy-response")

NTFY_USER = os.environ.get("NTFY_USER")
NTFY_PASSWORD = os.environ.get("NTFY_PASSWORD")
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

        # Try query commands first
        query_result = handle_query(message)

        if query_result is not None:
            return jsonify({
                "response": query_result
            })

        # Try inventory commands
        parsed = parse_inventory_command(message)

        if parsed:
            action, product_name, amount, unit = parsed

            result = change_stock(
                action,
                product_name,
                amount,
                unit
            )

            return jsonify({
                "response": result
            })

        # Unknown command
        return jsonify({
            "response": help_message()
        })

    except Exception as e:
        print(f"Web chat error: {e}")

        return jsonify({
            "response": f"❌ Error: {e}"
        }), 500

# ============================================================
# HTTP helpers
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


def ntfy_auth():
    if NTFY_USER and NTFY_PASSWORD:
        return (NTFY_USER, NTFY_PASSWORD)

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
# Grocy product handling
# ============================================================

def get_products():
    products = grocy_get("/api/objects/products")

    result = {}

    for product in products:
        result[product["name"].strip().lower()] = product

    return result


def find_product(product_name):
    products = get_products()

    name = product_name.strip().lower()

    # Exact match
    if name in products:
        return products[name]

    # Partial match
    matches = []

    for product_name_key, product in products.items():
        if name in product_name_key:
            matches.append(product)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        names = ", ".join(p["name"] for p in matches)

        raise ValueError(
            f"❌ Multiple products match '{product_name}': {names}"
        )

    return None


# ============================================================
# Unit handling
# ============================================================

UNIT_ALIASES = {
    "kg": "kilogram",
    "kgs": "kilogram",
    "kilogram": "kilogram",
    "kilograms": "kilogram",

    "g": "gram",
    "gm": "gram",
    "gms": "gram",
    "gram": "gram",
    "grams": "gram",

    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",

    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",

    "l": "litre",
    "liter": "litre",
    "liters": "litre",
    "litre": "litre",
    "litres": "litre",

    "gal": "gal",
    "gallon": "gal",
    "gallons": "gal",

    "piece": "Piece",
    "pieces": "Piece",
    "pc": "Piece",
    "pcs": "Piece",

    "pack": "Pack",
    "packs": "Pack",

    "slice": "slice",
    "slices": "slice",

    "stick": "stick",
    "sticks": "stick",
}


def normalize_unit(unit):
    if not unit:
        return None

    return UNIT_ALIASES.get(unit.strip().lower(), unit.strip())


def get_product_stock(product_id):
    return grocy_get(f"/api/stock/products/{product_id}")


def check_unit(product, entered_unit):
    stock = get_product_stock(product["id"])

    grocy_unit = stock["quantity_unit_stock"]["name"]

    normalized_entered = normalize_unit(entered_unit)

    if normalized_entered != grocy_unit:
        raise ValueError(
            f"❌ Unit mismatch for {product['name']}\n\n"
            f"Grocy stock unit: {grocy_unit}\n"
            f"You entered: {entered_unit}\n\n"
            f"Please use: {grocy_unit}"
        )

    return grocy_unit


# ============================================================
# Add / consume stock
# ============================================================

def change_stock(action, product_name, amount, unit):
    product = find_product(product_name)

    if not product:
        return f"❌ Product not found: {product_name}"

    try:
        grocy_unit = check_unit(product, unit)

        body = {
            "amount": amount
        }

        if action == "add":
            endpoint = f"/api/stock/products/{product['id']}/add"

            # Set best-before date to the product's normal
            # shelf-life when Grocy has one.
            shelf_life = product.get("default_best_before_days", 0) or 0

            if shelf_life > 0:
                best_before = (
                    date.today() + timedelta(days=shelf_life)
                ).isoformat()

                body["best_before_date"] = best_before

        else:
            endpoint = f"/api/stock/products/{product['id']}/consume"

        grocy_post(endpoint, body)

        stock = get_product_stock(product["id"])

        new_amount = stock["stock_amount_aggregated"]

        if action == "add":
            action_text = "Added"
        else:
            action_text = "Consumed"

        return (
            f"✅ Grocy updated\n\n"
            f"{product['name']}\n"
            f"{action_text}: {amount:g} {grocy_unit}\n"
            f"New stock: {new_amount:g} {grocy_unit}"
        )

    except requests.HTTPError as e:
        try:
            details = e.response.json()
            error_message = details.get(
                "error_message",
                e.response.text
            )
        except Exception:
            error_message = e.response.text

        return f"❌ Grocy error: {error_message}"

    except Exception as e:
        return f"❌ Error: {e}"

# ============================================================
# Product groups
# ============================================================

def get_product_groups():
    """
    Return Grocy product groups indexed by lowercase name.
    """
    groups = grocy_get("/api/objects/product_groups")

    result = {}

    for group in groups:
        name = group.get("name", "").strip()

        if name:
            result[name.lower()] = group

    return result


def find_product_group(group_name):
    """
    Find a product group by exact or partial name.
    """

    groups = get_product_groups()

    name = group_name.strip().lower()

    # Exact match
    if name in groups:
        return groups[name]

    # Partial match
    matches = []

    for group_name_key, group in groups.items():
        if name in group_name_key:
            matches.append(group)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        names = ", ".join(
            group["name"] for group in matches
        )

        raise ValueError(
            f"Multiple product groups match '{group_name}': {names}"
        )

    return None


def format_group_stock(group_name):
    """
    Return current stock for all products
    belonging to a Grocy product group.
    """

    group = find_product_group(group_name)

    if not group:
        return None

    group_id = group["id"]

    stock = grocy_get("/api/stock")

    if not stock:
        return (
            f"📦 {group['name']}\n\n"
            "No products are currently in stock."
        )

    # Get all products so we can determine
    # each product's product group.
    products = grocy_get("/api/objects/products")

    group_products = {}

    for product in products:
        if product.get("product_group_id") == group_id:
            group_products[product["id"]] = product

    if not group_products:
        return (
            f"📦 {group['name']}\n\n"
            "No products belong to this group."
        )

    # Quantity units
    units = grocy_get("/api/objects/quantity_units")

    unit_map = {
        unit["id"]: unit["name"]
        for unit in units
    }

    # Aggregate stock by product
    stock_by_product = {}

    for item in stock:
        product_id = item.get("product_id")

        if product_id not in group_products:
            continue

        amount = item.get(
            "amount_aggregated",
            item.get("amount", 0)
        )

        stock_by_product[product_id] = (
            stock_by_product.get(product_id, 0) + amount
        )

    lines = [
        f"📦 {group['name']}",
        ""
    ]

    found_stock = False

    for product_id in sorted(
        group_products,
        key=lambda pid: group_products[pid]["name"].lower()
    ):

        product = group_products[product_id]

        amount = stock_by_product.get(product_id, 0)

        unit = unit_map.get(
            product.get("qu_id_stock"),
            ""
        )

        lines.append(
            f"• {product['name']}: {amount:g}"
            + (f" {unit}" if unit else "")
        )

        found_stock = True

    if not found_stock:
        return (
            f"📦 {group['name']}\n\n"
            "No products are currently in stock."
        )

    return "\n".join(lines)

# ============================================================
# Stage 2 - Stock queries
# ============================================================

def format_single_stock(product_name):
    product = find_product(product_name)

    if not product:
        return f"❌ Product not found: {product_name}"

    stock = get_product_stock(product["id"])

    amount = stock["stock_amount_aggregated"]
    unit = stock["quantity_unit_stock"]["name"]

    location = stock.get("location")

    if location:
        location_name = location["name"]
    else:
        location_name = "Unknown"

    result = (
        f"📦 {product['name']}\n\n"
        f"Current stock: {amount:g} {unit}\n"
        f"Location: {location_name}"
    )

    next_due = stock.get("next_due_date")

    if next_due:
        result += f"\nNext due: {next_due}"

    return result


def format_all_stock():
    stock = grocy_get("/api/stock")

    if not stock:
        return "📦 No products are currently in stock."

    # Group by product in case Grocy returns
    # multiple stock entries.
    products = {}

    for item in stock:
        product = item.get("product", {})
        name = product.get("name", "Unknown")

        amount = item.get(
            "amount_aggregated",
            item.get("amount", 0)
        )

        unit = product.get(
            "qu_id_stock",
            ""
        )

        if name not in products:
            products[name] = {
                "amount": amount,
                "unit": unit,
            }

    # Get the actual stock units from product details.
    all_products = get_products()

    lines = ["📦 Current Stock", ""]

    for name in sorted(products.keys()):
        product = all_products.get(name.lower())

        if product:
            unit_id = product.get("qu_id_stock")

            try:
                units = grocy_get("/api/objects/quantity_units")

                unit_name = next(
                    (
                        u["name"]
                        for u in units
                        if u["id"] == unit_id
                    ),
                    ""
                )
            except Exception:
                unit_name = ""

        else:
            unit_name = ""

        amount = products[name]["amount"]

        if unit_name:
            lines.append(
                f"• {name}: {amount:g} {unit_name}"
            )
        else:
            lines.append(
                f"• {name}: {amount:g}"
            )

    return "\n".join(lines)


def format_low_stock():
    """
    Determine low stock using each product's
    configured min_stock_amount.
    """

    products = grocy_get("/api/objects/products")
    stock = grocy_get("/api/stock")

    stock_by_product = {}

    for item in stock:
        product_id = item["product_id"]

        amount = item.get(
            "amount_aggregated",
            item.get("amount", 0)
        )

        stock_by_product[product_id] = amount

    low = []

    for product in products:
        minimum = product.get("min_stock_amount", 0) or 0

        # Only consider products where a minimum
        # stock amount has actually been configured.
        if minimum <= 0:
            continue

        current = stock_by_product.get(
            product["id"],
            0
        )

        if current <= minimum:
            low.append(
                (
                    product["name"],
                    current,
                    minimum,
                    product["qu_id_stock"],
                )
            )

    if not low:
        return "✅ Nothing is currently at or below minimum stock."

    units = grocy_get("/api/objects/quantity_units")

    unit_map = {
        u["id"]: u["name"]
        for u in units
    }

    lines = ["⚠️ Low Stock", ""]

    for name, current, minimum, unit_id in sorted(low):
        unit = unit_map.get(unit_id, "")

        lines.append(
            f"• {name}: {current:g} {unit} "
            f"(minimum {minimum:g} {unit})"
        )

    return "\n".join(lines)


def format_shopping_list():
    shopping = grocy_get("/api/objects/shopping_list")

    if not shopping:
        return "🛒 Shopping list is empty."

    lines = ["🛒 Shopping List", ""]

    for item in shopping:
        product = item.get("product") or {}

        name = product.get(
            "name",
            item.get("name", "Unknown")
        )

        amount = item.get("amount", 1)

        unit = ""

        if product:
            unit_id = product.get("qu_id_stock")

            if unit_id:
                try:
                    units = grocy_get(
                        "/api/objects/quantity_units"
                    )

                    unit = next(
                        (
                            u["name"]
                            for u in units
                            if u["id"] == unit_id
                        ),
                        ""
                    )
                except Exception:
                    pass

        if unit:
            lines.append(
                f"• {name}: {amount:g} {unit}"
            )
        else:
            lines.append(
                f"• {name}: {amount:g}"
            )

    return "\n".join(lines)


# ============================================================
# Command parsing
# ============================================================

def parse_inventory_command(message):
    """
    Supported:

    + tomato 1 kg
    - tomato 0.5 kg
    """

    pattern = r"^([+-])\s+(.+?)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s*$"

    match = re.match(
        pattern,
        message.strip()
    )

    if not match:
        return None

    sign = match.group(1)
    product_name = match.group(2).strip()
    amount = float(match.group(3))
    unit = match.group(4).strip()

    if amount <= 0:
        return None

    action = "add" if sign == "+" else "consume"

    return action, product_name, amount, unit


def handle_query(message):
    command = message.strip()

    lower = command.lower()

    # All stock
    if lower == "stock":
        return format_all_stock()

    # Low stock
    if lower in (
        "low stock",
        "lowstock",
        "low"
    ):
        return format_low_stock()

    # Shopping list
    if lower in (
        "shopping list",
        "shopping",
        "shoppinglist"
    ):
        return format_shopping_list()

    # Individual product
    # Stock by product or product group
    if lower.startswith("stock "):

        search_name = command[6:].strip()

    if not search_name:
        return format_all_stock()

    # First check whether the name is a product group.
    group_result = format_group_stock(search_name)

    if group_result is not None:
        return group_result

    # Otherwise treat it as a product.
    return format_single_stock(search_name)


# ============================================================
# Help
# ============================================================

def help_message():
    return (
        "❓ Grocy Assistant Commands\n\n"
        "Inventory:\n"
        "+ tomato 1 kg\n"
        "- tomato 0.3 kg\n\n"
        "Queries:\n"
        "stock\n"
	"stock tomato\n"
	"stock vegetables\n"
	"stock rice\n"
	"low stock\n"
	"shopping list"
    )


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

            import time
            time.sleep(5)


# ============================================================
# Main processing
# ============================================================

def process_message(message):
    print(f"Received: {message}")

    # ----------------------------------------
    # Stage 2 queries
    # ----------------------------------------

    query_result = handle_query(message)

    if query_result is not None:
        print(query_result)
        print()

        notify(query_result)

        return

    # ----------------------------------------
    # Stage 1 inventory commands
    # ----------------------------------------

    parsed = parse_inventory_command(message)

    if parsed:
        action, product_name, amount, unit = parsed

        result = change_stock(
            action,
            product_name,
            amount,
            unit,
        )

        print(result)
        print()

        notify(result)

        return

    # ----------------------------------------
    # Invalid command
    # ----------------------------------------

    result = help_message()

    print(result)
    print()

    notify(result)


# ============================================================
# Main - Web Server
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
