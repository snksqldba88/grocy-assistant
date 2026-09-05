from assistant.responses import (
    success,
    error,
    info,
    warning,
    no_result,
    help_message,
)


def test_responses():

    print("\n=== SUCCESS ===")
    print(success("Grocy updated"))

    print("\n=== ERROR ===")
    print(error("Product not found"))

    print("\n=== INFO ===")
    print(info("No products found"))

    print("\n=== WARNING ===")
    print(warning("Low stock"))

    print("\n=== NO RESULT ===")
    print(no_result("Nothing matched"))

    print("\n=== HELP ===")
    print(help_message())


if __name__ == "__main__":
    test_responses()