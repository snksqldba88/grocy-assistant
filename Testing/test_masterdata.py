from assistant.masterdata import (
    lookup_product,
    lookup_product_group,
    format_product_info,
    format_product_group_info,
)


def test_product_lookup():
    print("\n=== PRODUCT LOOKUP ===")

    result = lookup_product("tomato")

    print(result)


def test_product_group_lookup():
    print("\n=== GROUP LOOKUP ===")

    result = lookup_product_group("vegetables")

    print(result)


def test_product_info():
    print("\n=== PRODUCT INFO ===")

    result = format_product_info("tomato")

    print(result)


def test_group_info():
    print("\n=== GROUP INFO ===")

    result = format_product_group_info("vegetables")

    print(result)


if __name__ == "__main__":
    test_product_lookup()
    test_product_group_lookup()
    test_product_info()
    test_group_info()