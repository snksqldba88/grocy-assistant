from grocy.products import find_product
from grocy.groups import find_product_group


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