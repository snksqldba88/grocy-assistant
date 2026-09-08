from grocy.api import grocy_get, grocy_post


# ============================================================
# Grocy product groups
# ============================================================

def get_product_groups():
    """
    Return Grocy product groups indexed by lowercase name.
    """

    groups = grocy_get(
        "/api/objects/product_groups"
    )

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
            group["name"]
            for group in matches
        )

        raise ValueError(
            f"Multiple product groups match "
            f"'{group_name}': {names}"
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
    products = grocy_get(
        "/api/objects/products"
    )

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
    units = grocy_get(
        "/api/objects/quantity_units"
    )

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
            stock_by_product.get(product_id, 0)
            + amount
        )

    lines = [
        f"📦 {group['name']}",
        ""
    ]

    found_stock = False

    for product_id in sorted(
        group_products,
        key=lambda pid:
            group_products[pid]["name"].lower()
    ):
        product = group_products[product_id]

        amount = stock_by_product.get(
            product_id,
            0
        )

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

def create_product_group(name):
    """
    Create a new product group in Grocy.

    Returns:
        Created product group response from Grocy.
    """

    body = {
        "name": name.strip(),
    }

    return grocy_post(
        "/api/objects/product_groups",
        body,
    )