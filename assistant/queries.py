from grocy.products import (
    find_product,
)

from grocy.stock import (
    get_product_stock,
    get_low_stock_products,
)

from grocy.groups import (
    format_group_stock,
)

from grocy.shopping import (
    format_shopping_list,
)

from grocy.api import (
    grocy_get,
)


# ============================================================
# Product stock query
# ============================================================

def query_product_stock(product_name):
    """
    Return current stock information for one product.

    Returns:
        Formatted response string.
    """

    try:
        product = find_product(product_name)

    except ValueError as e:
        return str(e)

    if not product:
        return (
            f"❌ Product not found: {product_name}"
        )

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


# ============================================================
# All stock query
# ============================================================

def query_all_stock():
    """
    Return current stock for all products.
    """

    stock = grocy_get("/api/stock")

    if not stock:
        return (
            "📦 No products are currently in stock."
        )

    products = {}

    for item in stock:
        product = item.get("product", {})

        name = product.get(
            "name",
            "Unknown"
        )

        amount = item.get(
            "amount_aggregated",
            item.get("amount", 0)
        )

        if name not in products:
            products[name] = {
                "amount": amount,
                "unit_id": product.get(
                    "qu_id_stock"
                ),
            }

    # Get quantity units once.
    try:
        units = grocy_get(
            "/api/objects/quantity_units"
        )

        unit_map = {
            unit["id"]: unit["name"]
            for unit in units
        }

    except Exception:
        unit_map = {}

    lines = [
        "📦 Current Stock",
        ""
    ]

    for name in sorted(
        products,
        key=str.lower
    ):
        item = products[name]

        amount = item["amount"]

        unit = unit_map.get(
            item["unit_id"],
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


# ============================================================
# Group stock query
# ============================================================

def query_group_stock(group_name):
    """
    Return current stock for a product group.

    Returns:
        Formatted response string or None
        if the group does not exist.
    """

    return format_group_stock(group_name)


# ============================================================
# Low stock query
# ============================================================

def query_low_stock():
    """
    Return products that are at or below
    their configured minimum stock amount.

    Returns:
        Formatted response string.
    """

    low_stock = get_low_stock_products()

    # get_low_stock_products() currently uses
    # amount < minimum. We will format the
    # returned structured data here.
    if not low_stock:
        return (
            "✅ Nothing is currently "
            "below minimum stock."
        )

    lines = [
        "⚠️ Low Stock",
        ""
    ]

    for item in low_stock:
        product = item["product"]
        amount = item["amount"]
        minimum = item["min_stock_amount"]
        unit = item["unit"]

        if unit:
            lines.append(
                f"• {product['name']}: "
                f"{amount:g} {unit} "
                f"(minimum {minimum:g} {unit})"
            )
        else:
            lines.append(
                f"• {product['name']}: "
                f"{amount:g} "
                f"(minimum {minimum:g})"
            )

    return "\n".join(lines)


# ============================================================
# Shopping list query
# ============================================================

def query_shopping_list():
    """
    Return the current Grocy shopping list.
    """

    return format_shopping_list()