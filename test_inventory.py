from assistant.inventory import handle_inventory_command


def test_command(message):
    print("\n" + "=" * 50)
    print(f"COMMAND: {message}")
    print("=" * 50)

    result = handle_inventory_command(message)

    print(result)


if __name__ == "__main__":

    test_command("+ tomato 0.1 kg")

    test_command("- tomato 0.1 kg")

    test_command("I bought 0.1 kg tomato")

    test_command("I used 0.1 kg tomato")

    test_command("Hello")