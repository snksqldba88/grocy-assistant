from grocy.products import find_product, create_product
from grocy.groups import find_product_group, create_product_group
from grocy.locations import find_location
from grocy.units import find_quantity_unit


# ============================================================
# Product lookup
# ============================================================

def lookup_product(product_name):
    """
    Find a Grocy product by exact or partial name.

    Returns:
        Product dictionary, or None if not found.
    """

    return find_product(product_name)


def add_product(
    name,
    product_group_id,
    location_id,
    qu_id_purchase,
    qu_id_stock,
):
    """
    Create a new Grocy product.

    Returns:
        Created product response from Grocy.
    """

    return create_product(
        name=name,
        product_group_id=product_group_id,
        location_id=location_id,
        qu_id_purchase=qu_id_purchase,
        qu_id_stock=qu_id_stock,
    )


# ============================================================
# Product group lookup
# ============================================================

def lookup_product_group(group_name):
    """
    Find a Grocy product group by exact or partial name.

    Returns:
        Product group dictionary, or None if not found.
    """

    return find_product_group(group_name)


def add_product_group(name):
    """
    Create a new Grocy product group.

    Returns:
        Created product group response from Grocy.
    """

    return create_product_group(name)


# ============================================================
# Product information
# ============================================================

def format_product_info(product_name):
    """
    Return basic information about a Grocy product.
    """

    product = lookup_product(product_name)

    if not product:
        return f"❌ Product not found: {product_name}"

    lines = [
        f"📦 {product['name']}",
        "",
        f"Product ID: {product['id']}",
    ]

    group_id = product.get("product_group_id")

    if group_id:
        lines.append(
            f"Product group ID: {group_id}"
        )

    unit_id = product.get("qu_id_stock")

    if unit_id:
        lines.append(
            f"Stock unit ID: {unit_id}"
        )

    return "\n".join(lines)


# ============================================================
# Product group information
# ============================================================

def format_product_group_info(group_name):
    """
    Return basic information about a Grocy product group.
    """

    group = lookup_product_group(group_name)

    if not group:
        return f"❌ Product group not found: {group_name}"

    return (
        f"📁 {group['name']}\n\n"
        f"Group ID: {group['id']}"
    )

def lookup_location(location_name):
    """
    Find a Grocy location by exact or partial name.
    """

    return find_location(location_name)


def lookup_quantity_unit(unit_name):
    """
    Find a Grocy quantity unit by exact or partial name.
    """

    return find_quantity_unit(unit_name)


# ============================================================
# Product list
# ============================================================

def list_products():
    from grocy.products import get_products

    products = get_products()

    if not products:
        return "📦 No products found."

    names = sorted(
        product["name"]
        for product in products.values()
    )

    lines = ["📦 Products", ""]

    for index, name in enumerate(names, start=1):
        lines.append(f"{index}. {name}")

    return "\n".join(lines)


# ============================================================
# Product group list
# ============================================================

def list_product_groups():
    from grocy.groups import get_product_groups

    groups = get_product_groups()

    if not groups:
        return "📁 No product groups found."

    names = sorted(
        group["name"]
        for group in groups.values()
    )

    lines = ["📁 Product Groups", ""]

    for index, name in enumerate(names, start=1):
        lines.append(f"{index}. {name}")

    return "\n".join(lines)