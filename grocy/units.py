from grocy.api import grocy_get


# ============================================================
# Grocy quantity units
# ============================================================

def get_quantity_units():
    """
    Return active Grocy quantity units indexed by lowercase name.
    """

    units = grocy_get(
        "/api/objects/quantity_units"
    )

    result = {}

    for unit in units:
        name = unit.get("name", "").strip()

        if name and unit.get("active", 1):
            result[name.lower()] = unit

    return result


def find_quantity_unit(unit_name):
    """
    Find a Grocy quantity unit by exact or partial name.
    """

    units = get_quantity_units()

    name = unit_name.strip().lower()

    # Exact match
    if name in units:
        return units[name]

    # Partial match
    matches = []

    for unit_name_key, unit in units.items():
        if name in unit_name_key:
            matches.append(unit)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        names = ", ".join(
            unit["name"]
            for unit in matches
        )

        raise ValueError(
            f"Multiple quantity units match "
            f"'{unit_name}': {names}"
        )

    return None