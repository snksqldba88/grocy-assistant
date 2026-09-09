from assistant.conversation import ConversationState

from assistant.masterdata import (
    lookup_product_group,
    lookup_location,
    lookup_quantity_unit,
    add_product,
    add_product_group,
)

from assistant.parser import (
    parse_natural_stock_query,
    is_natural_low_stock_query,
    parse_shopping_add_command,
    parse_shopping_remove_command,
)

from assistant.inventory import (
    handle_inventory_command,
)

from grocy.shopping import (
    add_to_shopping_list,
    remove_from_shopping_list,
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


    # command = parse_shopping_add_command(message)
    #
    # if command:
    #     _, product_name, amount, unit = command
    #     return add_to_shopping_list(product_name, amount)
    #
    # command = parse_shopping_remove_command(message)
    #
    # if command:
    #     _, product_name, amount, unit = command
    #     return remove_from_shopping_list(product_name, amount)

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
conversation = ConversationState()

def process_message(message):
    if not message or not message.strip():
        return help_message()

    text = message.strip().lower()

    # --------------------------------------------------------
    # Active conversation
    # --------------------------------------------------------

    if conversation.active:
        if conversation.flow == "add_product":

            if conversation.step == "product_name":
                conversation.data["name"] = message.strip()
                conversation.step = "product_group"

                return (
                    "📦 Product name: "
                    f"{conversation.data['name']}\n\n"
                    "Which product group should it belong to?"
                )

            if conversation.step == "product_group":
                group = lookup_product_group(message.strip())

                if not group:
                    return (
                        f"❌ Product group not found: {message.strip()}\n\n"
                        "Please enter a valid product group."
                    )

                conversation.data["product_group_id"] = group["id"]
                conversation.data["product_group_name"] = group["name"]
                conversation.step = "location"

                return (
                    "📁 Product group: "
                    f"{group['name']}\n\n"
                    "Which location should it be stored in?"
                )

            if conversation.step == "location":
                location = lookup_location(message.strip())

                if not location:
                    return (
                        f"❌ Location not found: {message.strip()}\n\n"
                        "Please enter a valid location."
                    )

                conversation.data["location_id"] = location["id"]
                conversation.data["location_name"] = location["name"]
                conversation.step = "purchase_unit"

                return (
                    "📍 Location: "
                    f"{location['name']}\n\n"
                    "What is the purchase unit?"
                )

            if conversation.step == "purchase_unit":
                unit = lookup_quantity_unit(message.strip())

                if not unit:
                    return (
                        f"❌ Quantity unit not found: {message.strip()}\n\n"
                        "Please enter a valid quantity unit."
                    )

                conversation.data["qu_id_purchase"] = unit["id"]
                conversation.data["purchase_unit_name"] = unit["name"]
                conversation.step = "stock_unit"

                return (
                    "📏 Purchase unit: "
                    f"{unit['name']}\n\n"
                    "What is the stock unit?"
                )

            if conversation.step == "stock_unit":
                unit = lookup_quantity_unit(message.strip())

                if not unit:
                    return (
                        f"❌ Quantity unit not found: {message.strip()}\n\n"
                        "Please enter a valid quantity unit."
                    )

                conversation.data["qu_id_stock"] = unit["id"]
                conversation.data["stock_unit_name"] = unit["name"]
                conversation.step = "confirmation"

                return (
                    "📏 Stock unit: "
                    f"{unit['name']}\n\n"
                    "Please confirm the product details:\n\n"
                    f"📦 Product: {conversation.data['name']}\n"
                    f"📁 Group: {conversation.data['product_group_name']}\n"
                    f"📍 Location: {conversation.data['location_name']}\n"
                    f"🛒 Purchase unit: {conversation.data['purchase_unit_name']}\n"
                    f"📦 Stock unit: {conversation.data['stock_unit_name']}\n\n"
                    "Create this product? (yes/no)"
                )

            if conversation.step == "confirmation":
                if message.strip().lower() in {
                    "yes",
                    "y",
                    "confirm",
                }:
                    result = add_product(
                        name=conversation.data["name"],
                        product_group_id=conversation.data["product_group_id"],
                        location_id=conversation.data["location_id"],
                        qu_id_purchase=conversation.data["qu_id_purchase"],
                        qu_id_stock=conversation.data["qu_id_stock"],
                    )

                    product_name = conversation.data["name"]

                    conversation.end()

                    return (
                        f"✅ Product created successfully!\n\n"
                        f"📦 {product_name}"
                    )

                if message.strip().lower() in {
                    "no",
                    "n",
                    "cancel",
                }:
                    conversation.end()

                    return (
                        "❌ Product creation cancelled.\n\n"
                        "No changes were made to Grocy."
                    )

                return (
                    "Please answer with **yes** or **no**."
                )

        if conversation.flow == "add_product_group":

            if conversation.step == "group_name":
                conversation.data["name"] = message.strip()
                conversation.step = "group_confirmation"

                return (
                    "📁 Product group name: "
                    f"{conversation.data['name']}\n\n"
                    "Create this product group? (yes/no)"
                )

            if conversation.flow == "add_product_group":

                if conversation.step == "group_confirmation":

                    if message.strip().lower() in {
                        "yes",
                        "y",
                        "confirm",
                    }:
                        result = add_product_group(
                            conversation.data["name"]
                        )

                        group_name = conversation.data["name"]

                        conversation.end()

                        return (
                            "✅ Product group created successfully!\n\n"
                            f"📁 {group_name}"
                        )

                    if message.strip().lower() in {
                        "no",
                        "n",
                        "cancel",
                    }:
                        conversation.end()

                        return (
                            "❌ Product group creation cancelled.\n\n"
                            "No changes were made to Grocy."
                        )

                    return (
                        "Please answer with **yes** or **no**."
                    )

    # --------------------------------------------------------
    # Start product group creation
    # --------------------------------------------------------

    if text in {
        "add product group",
        "new product group",
        "create product group",
    }:
        conversation.start("add_product_group")
        conversation.step = "group_name"

        return (
            "📁 Let's create a new product group.\n\n"
            "What is the group name?"
        )

    # --------------------------------------------------------
    # Start product creation
    # --------------------------------------------------------

    if text in {
        "add product",
        "new product",
        "create product",
    }:
        conversation.start("add_product")
        conversation.step = "product_name"

        return (
            "📦 Let's create a new product.\n\n"
            "What is the product name?"
        )

    shopping_add = parse_shopping_add_command(message)

    if shopping_add:
        _, product_name, amount, unit = shopping_add
        return add_to_shopping_list(product_name, amount)

    shopping_remove = parse_shopping_remove_command(message)

    if shopping_remove:
        _, product_name, amount, unit = shopping_remove
        return remove_from_shopping_list(product_name, amount)

    inventory_result = handle_inventory_command(message)

    if inventory_result is not None:
        return inventory_result

    query_result = handle_query(message)

    if query_result is not None:
        return query_result

    return help_message()