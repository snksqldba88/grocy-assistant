from grocy.api import grocy_get


# ============================================================
# Shopping list
# ============================================================

def format_shopping_list():
    shopping = grocy_get(
        "/api/objects/shopping_list"
    )

    if not shopping:
        return "🛒 Shopping list is empty."

    lines = [
        "🛒 Shopping List",
        ""
    ]

    for item in shopping:
        product = item.get("product") or {}

        name = product.get(
            "name",
            item.get("name", "Unknown")
        )

        amount = item.get("amount", 1)

        unit = ""

        if product:
            unit_id = product.get("qu_id_stock")

            if unit_id:
                try:
                    units = grocy_get(
                        "/api/objects/quantity_units"
                    )

                    unit = next(
                        (
                            u["name"]
                            for u in units
                            if u["id"] == unit_id
                        ),
                        ""
                    )

                except Exception:
                    pass

        if unit:
            lines.append(
                f"• {name}: {amount:g} {unit}"
            )
        else:
            lines.append(
                f"• {name}: {amount:g}"
            )

    return "\n".join(lines)