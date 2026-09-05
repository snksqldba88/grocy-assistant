from assistant.parser import (
    parse_natural_stock_query,
    is_natural_low_stock_query,
)

from assistant.inventory import (
    handle_inventory_command,
)

from assistant.queries import (
    query_product_stock,
    query_all_stock,
    query_group_stock,
    query_low_stock,
    query_shopping_list,
)

from assistant.responses import (
    help_message,
)


# ============================================================
# Query handling
# ============================================================

def handle_query(message):
    """
    Handle stock and other information queries.

    Returns:
        Response string, or None if the message
        is not a recognized query.
    """

    text = message.strip().lower()

    # --------------------------------------------------------
    # Low stock
    # --------------------------------------------------------

    if is_natural_low_stock_query(message):
        return query_low_stock()

    # --------------------------------------------------------
    # Shopping list
    # --------------------------------------------------------

    if text in {
        "shopping list",
        "shopping",
        "what is on my shopping list",
        "what's on my shopping list",
        "whats on my shopping list",
    }:
        return query_shopping_list()

    # --------------------------------------------------------
    # All stock
    # --------------------------------------------------------

    if text in {
        "stock",
        "inventory",
        "all stock",
        "show stock",
        "show inventory",
    }:
        return query_all_stock()

    # --------------------------------------------------------
    # Explicit stock command
    # --------------------------------------------------------

    if text.startswith("stock "):
        search_name = message.strip()[6:].strip()

        if not search_name:
            return query_all_stock()

        # Check product group first, preserving the
        # behavior of the existing application.
        group_result = query_group_stock(search_name)

        if group_result is not None:
            return group_result

        return query_product_stock(search_name)

    # --------------------------------------------------------
    # Natural stock query
    # --------------------------------------------------------

    search_name = parse_natural_stock_query(message)

    if search_name:
        # First try product lookup.
        result = query_product_stock(search_name)

        # If product was not found, try product group.
        if result.startswith("❌ Product not found"):
            group_result = query_group_stock(search_name)

            if group_result:
                return group_result

        return result

    return None


# ============================================================
# Main assistant engine
# ============================================================

def process_message(message):
    """
    Process a user message and return the appropriate response.

    The engine checks inventory commands first, followed by
    queries, and finally falls back to the help message.
    """

    if not message or not message.strip():
        return help_message()

    # --------------------------------------------------------
    # Inventory commands
    # --------------------------------------------------------

    inventory_result = handle_inventory_command(message)

    if inventory_result is not None:
        return inventory_result

    # --------------------------------------------------------
    # Queries
    # --------------------------------------------------------

    query_result = handle_query(message)

    if query_result is not None:
        return query_result

    # --------------------------------------------------------
    # Unknown command
    # --------------------------------------------------------

    return help_message()