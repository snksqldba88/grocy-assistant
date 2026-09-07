import re


# ============================================================
# Natural language inventory parsing
# ============================================================

def parse_natural_add_command(message):
    """
    Parse natural-language requests to add stock.

    Examples:

    I bought 2 kg of tomato
    Add 1 kg of rice
    I purchased 500 grams of onion
    We got 3 packs of bread

    Returns:
        ("add", product_name, amount, unit)
        or None
    """

    text = message.strip().lower()

    patterns = [
        # ----------------------------------------------------
        # I bought 2 kg of tomato
        # I bought 2 kg tomato
        # ----------------------------------------------------
        r"^i\s+bought\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # I purchased 2 kg of tomato
        # ----------------------------------------------------
        r"^i\s+purchased\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # I got 2 kg of tomato
        # We got 2 kg of tomato
        # ----------------------------------------------------
        r"^(?:i|we)\s+got\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # Add 2 kg of tomato
        # Add 2 kg tomato
        # ----------------------------------------------------
        r"^add\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # Please add 2 kg of tomato
        # ----------------------------------------------------
        r"^please\s+add\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, text)

        if not match:
            continue

        amount = float(match.group(1))
        unit = match.group(2).strip()
        product_name = match.group(3).strip()

        # Remove trailing punctuation.
        product_name = re.sub(
            r"[?.!,]+$",
            "",
            product_name
        ).strip()

        if amount <= 0:
            return None

        if not product_name:
            return None

        return (
            "add",
            product_name,
            amount,
            unit,
        )

    return None


# ============================================================
# Natural language stock consumption
# ============================================================

def parse_natural_consume_command(message):
    """
    Parse natural-language requests to consume/remove stock.

    Examples:

    I used 500 g of tomato
    I consumed 1 kg of rice
    We used 2 pieces of bread
    Remove 0.5 kg of tomato
    I finished 1 pack of bread

    Returns:
        ("consume", product_name, amount, unit)
        or None
    """

    text = message.strip().lower()

    patterns = [
        # ----------------------------------------------------
        # I used 2 kg of tomato
        # I used 2 kg tomato
        # ----------------------------------------------------
        r"^(?:i|we)\s+used\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # I consumed 2 kg of tomato
        # ----------------------------------------------------
        r"^(?:i|we)\s+consumed\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # I finished 1 pack of bread
        # ----------------------------------------------------
        r"^(?:i|we)\s+finished\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # Remove 2 kg of tomato
        # ----------------------------------------------------
        r"^remove\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # Please remove 2 kg of tomato
        # ----------------------------------------------------
        r"^please\s+remove\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # Consume 2 kg of tomato
        # ----------------------------------------------------
        r"^consume\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",

        # ----------------------------------------------------
        # Please consume 2 kg of tomato
        # ----------------------------------------------------
        r"^please\s+consume\s+(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:of\s+)?(.+?)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, text)

        if not match:
            continue

        amount = float(match.group(1))
        unit = match.group(2).strip()
        product_name = match.group(3).strip()

        # Remove trailing punctuation.
        product_name = re.sub(
            r"[?.!,]+$",
            "",
            product_name
        ).strip()

        if amount <= 0:
            return None

        if not product_name:
            return None

        return (
            "consume",
            product_name,
            amount,
            unit,
        )

    return None


def parse_inventory_command(message):
    """
    Supported:

    + tomato 1 kg
    - tomato 0.5 kg
    """

    pattern = r"^([+-])\s+(.+?)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s*$"

    match = re.match(
        pattern,
        message.strip()
    )

    if not match:
        return None

    sign = match.group(1)
    product_name = match.group(2).strip()
    amount = float(match.group(3))
    unit = match.group(4).strip()

    if amount <= 0:
        return None

    action = "add" if sign == "+" else "consume"

    return action, product_name, amount, unit


def parse_natural_stock_query(message):
    """
    Convert common natural-language stock questions
    into a product/group search term.

    Returns:
        search_name
        None if the message is not recognized
    """

    text = message.strip().lower()

    patterns = [
        # ----------------------------------------------------
        # How much X do I have?
        # ----------------------------------------------------
        r"^how much (?:of )?(.+?) do i have\??$",
        r"^how much (?:of )?(.+?) is there\??$",

        # ----------------------------------------------------
        # How many X do I have?
        # ----------------------------------------------------
        r"^how many (.+?) do i have\??$",
        r"^how many (.+?) are there\??$",

        # ----------------------------------------------------
        # Do I have X?
        # ----------------------------------------------------
        r"^do i have (?:any )?(.+?)\??$",
        r"^have i got (?:any )?(.+?)\??$",

        # ----------------------------------------------------
        # What X do I have?
        # ----------------------------------------------------
        r"^what (.+?) do i have\??$",

        # ----------------------------------------------------
        # What do I have in X?
        # ----------------------------------------------------
        r"^what do i have (?:in|for|of) (?:my )?(.+?)\??$",

        # ----------------------------------------------------
        # What's in X?
        # ----------------------------------------------------
        r"^what(?:'s| is) in (?:my )?(.+?)\??$",

        # ----------------------------------------------------
        # Show me X
        # ----------------------------------------------------
        r"^show me (?:my )?(.+?)$",
        r"^show (?:my )?(.+?)$",

        # ----------------------------------------------------
        # What's my X?
        # ----------------------------------------------------
        r"^what(?:'s| is) my (.+?)\??$",

        # ----------------------------------------------------
        # X stock
        # ----------------------------------------------------
        r"^what(?:'s| is) (?:my )?(.+?) stock\??$",
        r"^(.+?) stock\??$",
    ]

    for pattern in patterns:
        match = re.match(pattern, text)

        if match:
            search_name = match.group(1).strip()

            # Remove common trailing words.
            search_name = re.sub(
                r"\s+(available|left|remaining)$",
                "",
                search_name
            ).strip()

            # Remove common wording that isn't part
            # of the product/group name.
            search_name = re.sub(
                r"^(?:any|some|my)\s+",
                "",
                search_name
            ).strip()

            if search_name:
                return search_name

    return None


def is_natural_low_stock_query(message):
    text = message.strip().lower()

    patterns = [
        r"^what(?:'s|s| is) running low\??$",
        r"^what is low\??$",
        r"^what items are low\??$",
        r"^which items are low\??$",
        r"^which products are low\??$",
        r"^what products are low\??$",
        r"^what do i need to restock\??$",
        r"^what needs restocking\??$",
        r"^what do i need to buy\??$",
    ]

    return any(
        re.match(pattern, text)
        for pattern in patterns
    )

def parse_shopping_add_command(message):
    text = message.strip().lower()

    patterns = [
        r"^add\s+(.+?)\s+(\d+(?:\.\d+)?)\s*(kg|kilogram|g|gram|lb|lbs|pound|pounds|l|litre|liter|gal|gallon|piece|pieces|pack|packs)\s+to\s+shopping\s+list$",
        r"^add\s+(\d+(?:\.\d+)?)\s*(kg|kilogram|g|gram|lb|lbs|pound|pounds|l|litre|liter|gal|gallon|piece|pieces|pack|packs)\s+(.+?)\s+to\s+shopping\s+list$",
    ]

    for i, pattern in enumerate(patterns):
        match = re.match(pattern, text)

        if not match:
            continue

        if i == 0:
            product_name = match.group(1)
            amount = float(match.group(2))
            unit = match.group(3)
        else:
            amount = float(match.group(1))
            unit = match.group(2)
            product_name = match.group(3)

        return (
            "add_shopping",
            product_name,
            amount,
            unit,
        )

    return None


def parse_shopping_remove_command(message):
    text = message.strip().lower()

    patterns = [
        r"^remove\s+(.+?)\s+(\d+(?:\.\d+)?)\s*(kg|kilogram|g|gram|lb|lbs|pound|pounds|l|litre|liter|gal|gallon|piece|pieces|pack|packs)\s+from\s+shopping\s+list$",
        r"^remove\s+(\d+(?:\.\d+)?)\s*(kg|kilogram|g|gram|lb|lbs|pound|pounds|l|litre|liter|gal|gallon|piece|pieces|pack|packs)\s+(.+?)\s+from\s+shopping\s+list$",
    ]

    for i, pattern in enumerate(patterns):
        match = re.match(pattern, text)

        if not match:
            continue

        if i == 0:
            product_name = match.group(1)
            amount = float(match.group(2))
            unit = match.group(3)
        else:
            amount = float(match.group(1))
            unit = match.group(2)
            product_name = match.group(3)

        return (
            "remove_shopping",
            product_name,
            amount,
            unit,
        )

    return None