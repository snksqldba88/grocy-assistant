# ============================================================
# Common response formatting
# ============================================================

def success(message):
    """
    Format a successful operation response.
    """

    return f"✅ {message}"


def error(message):
    """
    Format an error response.
    """

    return f"❌ {message}"


def info(message):
    """
    Format an informational response.
    """

    return f"ℹ️ {message}"


def warning(message):
    """
    Format a warning response.
    """

    return f"⚠️ {message}"


def no_result(message):
    """
    Format a response when no matching result exists.
    """

    return f"ℹ️ {message}"


def help_message():
    """
    Return the assistant help message.
    """

    return (
        "🤖 Grocy Assistant Commands\n\n"

        "Inventory:\n"
        "+ tomato 1 kg\n"
        "- tomato 0.3 kg\n\n"

        "Queries:\n"
        "stock\n"
        "stock tomato\n"
        "stock vegetables\n"
        "stock rice\n"
        "low stock\n"
        "shopping list"
    )