from assistant.engine import process_message


def test_message(message, expected_contains):
    print(f"\n>>> {message}")

    try:
        result = process_message(message)

        print(result)

        if expected_contains.lower() in result.lower():
            print("✅ PASS")
        else:
            print(
                f"❌ FAIL - expected to contain: "
                f"{expected_contains}"
            )

    except Exception as e:
        print(f"❌ ERROR: {e}")


# ============================================================
# Inventory
# ============================================================

test_message(
    "+ tomato 1 kg",
    "tomato",
)

test_message(
    "- tomato 0.3 kg",
    "tomato",
)


# ============================================================
# Stock queries
# ============================================================

test_message(
    "stock",
    "stock",
)

test_message(
    "stock tomato",
    "tomato",
)

test_message(
    "stock vegetables",
    "vegetables",
)


# ============================================================
# Low stock
# ============================================================

test_message(
    "what's running low",
    "low",
)

test_message(
    "what’s running low",
    "low",
)

test_message(
    "what's running low?",
    "low",
)

test_message(
    "what’s running low?",
    "low",
)


# ============================================================
# Shopping list
# ============================================================

test_message(
    "shopping list",
    "shopping",
)

test_message(
    "+ rice 2 kg",
    "rice",
)

test_message(
    "- rice 1 kg",
    "rice",
)


# ============================================================
# Unknown command
# ============================================================

test_message(
    "hello",
    "commands",
)