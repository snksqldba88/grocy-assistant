from assistant.parser import (
    parse_inventory_command,
    parse_natural_add_command,
    parse_natural_consume_command,
)

from grocy.stock import change_stock


# ============================================================
# Inventory command handling
# ============================================================

def handle_inventory_command(message):
    """
    Parse and execute an inventory command.

    Supports:
        + tomato 1 kg
        - tomato 0.5 kg
        I bought 2 kg tomato
        We got 1 kg rice
        I used 0.5 kg tomato

    Returns:
        Grocy response string, or None if the message
        is not an inventory command.
    """

    # --------------------------------------------------------
    # Symbol commands
    # --------------------------------------------------------

    command = parse_inventory_command(message)

    if command:
        action, product_name, amount, unit = command

        return change_stock(
            action,
            product_name,
            amount,
            unit,
        )

    # --------------------------------------------------------
    # Natural add commands
    # --------------------------------------------------------

    command = parse_natural_add_command(message)

    if command:
        action, product_name, amount, unit = command

        return change_stock(
            action,
            product_name,
            amount,
            unit,
        )

    # --------------------------------------------------------
    # Natural consume commands
    # --------------------------------------------------------

    command = parse_natural_consume_command(message)

    if command:
        action, product_name, amount, unit = command

        return change_stock(
            action,
            product_name,
            amount,
            unit,
        )

    # Not an inventory command
    return None