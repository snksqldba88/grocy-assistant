from grocy.api import (
    grocy_get,
    grocy_post,
)

from grocy.products import find_product


def format_shopping_list():
    shopping = grocy_get(
        "/api/objects/shopping_list"
    )

    if not shopping:
        return "🛒 Shopping list is empty."

    products = grocy_get(
        "/api/objects/products"
    )

    product_map = {
        product["id"]: product
        for product in products
    }

    units = grocy_get(
        "/api/objects/quantity_units"
    )

    unit_map = {
        unit["id"]: unit["name"]
        for unit in units
    }

    lines = [
        "🛒 Shopping List",
        ""
    ]

    for item in shopping:
        product = product_map.get(
            item.get("product_id")
        )

        if not product:
            name = f"Unknown product ({item.get('product_id')})"
        else:
            name = product["name"]

        amount = item.get("amount", 0)

        unit = unit_map.get(
            item.get("qu_id"),
            ""
        )

        if unit:
            lines.append(
                f"• {name}: {amount:g} {unit}"
            )
        else:
            lines.append(
                f"• {name}: {amount:g}"
            )

    return "\n".join(lines)

def add_to_shopping_list(product_name, amount=1):
    try:
        product = find_product(product_name)
    except ValueError as e:
        return str(e)

    if not product:
        return f"❌ Product not found: {product_name}"

    try:
        grocy_post(
            "/api/stock/shoppinglist/add-product",
            {
                "product_id": product["id"],
                "product_amount": amount,
            },
        )
    except Exception as e:
        return f"❌ Could not add {product['name']} to shopping list: {e}"

    return (
        f"✅ Added {amount:g} of {product['name']} "
        "to the shopping list."
    )

    # return (
    #     f"✅ Added {amount:g} {product.get('qu_id_purchase', '')}"
    #     f" of {product['name']} to the shopping list."
    # )


def remove_from_shopping_list(product_name, amount=None):
    try:
        product = find_product(product_name)
    except ValueError as e:
        return str(e)

    if not product:
        return f"❌ Product not found: {product_name}"

    try:
        body = {
            "product_id": product["id"],
            "product_amount": amount,
        }

        if amount is not None:
            body["amount"] = amount

        grocy_post(
            "/api/stock/shoppinglist/remove-product",
            body,
        )

    except Exception as e:
        return (
            f"❌ Could not remove {product['name']} "
            f"from shopping list: {e}"
        )

    return f"✅ Removed {product['name']} from the shopping list."