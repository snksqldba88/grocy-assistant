from assistant.engine import process_message


def test_command(message):
    print("\n" + "=" * 60)
    print(f"COMMAND: {message}")
    print("=" * 60)

    result = process_message(message)

    print(result)


if __name__ == "__main__":

    # Inventory
    test_command("+ tomato 0.1 kg")
    test_command("- tomato 0.1 kg")

    # Stock queries
    test_command("stock")
    test_command("stock tomato")
    test_command("stock vegetables")

    # Low stock
    test_command("low stock")
    test_command("What's running low?")
    test_command("whats running low")

    # Shopping list
    test_command("shopping list")

    # Unknown
    test_command("hello")