# This is working monolithic version before assistant-layer integration
import re
import json
import requests
from flask import Flask, request, jsonify, render_template
from datetime import date, timedelta

from config import (
    GROCY_URL,
    GROCY_API_KEY,
    NTFY_URL,
    NTFY_INPUT_TOPIC,
    NTFY_RESPONSE_TOPIC,
    NTFY_USER,
    NTFY_PASSWORD,
)

from grocy.api import (
    grocy_get,
    grocy_post,
)

from grocy.products import (
    get_products,
    find_product,
)

from grocy.stock import (
    change_stock,
    get_product_stock,
)

from grocy.groups import (
    format_group_stock,
)

from grocy.shopping import (
    format_shopping_list,
)

from assistant.parser import (
    parse_natural_add_command,
    parse_natural_consume_command,
    parse_inventory_command,
    parse_natural_stock_query,
    is_natural_low_stock_query,
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

        # Try natural-language stock addition
        parsed = parse_natural_add_command(message)

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

        # Try natural-language stock consumption
        parsed = parse_natural_consume_command(message)

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


# ============================================================
# Natural language stock addition
# ============================================================




def handle_query(message):
    command = message.strip()
    lower = command.lower()

    # ========================================================
    # Help
    # ========================================================

    if lower in (
        "help",
        "?",
        "commands"
    ):
        return help_message()

    # ========================================================
    # All stock
    # ========================================================

    if lower == "stock":
        return format_all_stock()

    # ========================================================
    # Low stock - existing commands
    # ========================================================

    if lower in (
        "low stock",
        "lowstock",
        "low"
    ):
        return format_low_stock()

    # ========================================================
    # Low stock - natural language
    # ========================================================

    if is_natural_low_stock_query(command):
        return format_low_stock()

    # ========================================================
    # Shopping list
    # ========================================================

    if lower in (
        "shopping list",
        "shopping",
        "shoppinglist"
    ):
        return format_shopping_list()

    # ========================================================
    # Existing stock command
    # ========================================================

    if lower.startswith("stock "):

        search_name = command[6:].strip()

        if not search_name:
            return format_all_stock()

        # First check whether this is a product group.
        group_result = format_group_stock(search_name)

        if group_result is not None:
            return group_result

        # Otherwise treat it as an individual product.
        return format_single_stock(search_name)

    # ========================================================
    # Natural-language stock query
    # ========================================================

    search_name = parse_natural_stock_query(command)

    if search_name:

        # First check whether the search term is a
        # product group.
        group_result = format_group_stock(search_name)

        if group_result is not None:
            return group_result

        # Otherwise treat it as an individual product.
        return format_single_stock(search_name)

    # ========================================================
    # Not a query
    # ========================================================

    return None

# ============================================================
# Natural language stock query parsing
# ============================================================


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
        "shopping list\n\n"

        "You can also ask naturally:\n"
        "How much tomato do I have?\n"
        "Do I have rice?\n"
        "What vegetables do I have?\n"
        "Show me my spices\n"
        "What's running low?"
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
    # Stage 2.2A natural-language stock addition
    # ----------------------------------------

    parsed = parse_natural_add_command(message)

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
    # Stage 2.2B natural-language consumption
    # ----------------------------------------

    parsed = parse_natural_consume_command(message)

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
