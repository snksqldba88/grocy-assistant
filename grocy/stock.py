from datetime import date, timedelta

import requests

from grocy.api import grocy_get, grocy_post
from grocy.products import find_product


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

    return UNIT_ALIASES.get(
        unit.strip().lower(),
        unit.strip()
    )


def get_product_stock(product_id):
    return grocy_get(
        f"/api/stock/products/{product_id}"
    )

def get_low_stock_products():
    """
    Return products whose current aggregated stock
    is below their configured minimum stock amount.

    Returns:
        List of dictionaries containing:
        - product
        - amount
        - min_stock_amount
        - unit
    """

    stock = grocy_get("/api/stock")

    if not stock:
        return []

    # Get quantity units once.
    units = grocy_get(
        "/api/objects/quantity_units"
    )

    unit_map = {
        unit["id"]: unit["name"]
        for unit in units
    }

    low_stock = []

    for item in stock:
        product = item.get("product")

        if not product:
            continue

        amount = float(
            item.get(
                "amount_aggregated",
                item.get("amount", 0)
            ) or 0
        )

        min_stock = float(
            product.get(
                "min_stock_amount",
                0
            ) or 0
        )

        # Ignore products with no minimum stock configured.
        if min_stock <= 0:
            continue

        if amount <= min_stock:
            unit = unit_map.get(
                product.get("qu_id_stock"),
                ""
            )

            low_stock.append({
                "product": product,
                "amount": amount,
                "min_stock_amount": min_stock,
                "unit": unit,
            })

    # Sort alphabetically by product name.
    low_stock.sort(
        key=lambda item:
            item["product"]["name"].lower()
    )

    return low_stock


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
            endpoint = (
                f"/api/stock/products/{product['id']}/add"
            )

            # Set best-before date to the product's normal
            # shelf-life when Grocy has one.
            shelf_life = (
                product.get(
                    "default_best_before_days",
                    0
                ) or 0
            )

            if shelf_life > 0:
                best_before = (
                    date.today()
                    + timedelta(days=shelf_life)
                ).isoformat()

                body["best_before_date"] = best_before

        else:
            endpoint = (
                f"/api/stock/products/{product['id']}/consume"
            )

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