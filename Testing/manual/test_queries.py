from assistant.queries import (
    query_product_stock,
    query_all_stock,
    query_group_stock,
    query_low_stock,
    query_shopping_list,
)


def test_product_stock():
    print("\n=== PRODUCT STOCK ===")
    result = query_product_stock("tomato")
    print(result)


def test_all_stock():
    print("\n=== ALL STOCK ===")
    result = query_all_stock()
    print(result)


def test_group_stock():
    print("\n=== GROUP STOCK ===")
    result = query_group_stock("vegetables")
    print(result)


def test_low_stock():
    print("\n=== LOW STOCK ===")
    result = query_low_stock()
    print(result)


def test_shopping_list():
    print("\n=== SHOPPING LIST ===")
    result = query_shopping_list()
    print(result)


if __name__ == "__main__":
    test_product_stock()
    test_all_stock()
    test_group_stock()
    test_low_stock()
    test_shopping_list()