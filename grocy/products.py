from grocy.api import grocy_get, grocy_post


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
        names = ", ".join(
            p["name"] for p in matches
        )

        raise ValueError(
            f"❌ Multiple products match '{product_name}': {names}"
        )

    return None

# ============================================================
# Grocy product creation
# ============================================================

def create_product(
    name,
    location_id,
    product_group_id,
    qu_id_purchase,
    qu_id_stock,
):
    """
    Create a new product in Grocy.

    Returns:
        Created product response from Grocy.
    """

    body = {
        "name": name.strip(),
        "location_id": location_id,
        "qu_id_purchase": qu_id_purchase,
        "qu_id_stock": qu_id_stock,
        "product_group_id": product_group_id,
    }

    return grocy_post(
        "/api/objects/products",
        body,
    )
