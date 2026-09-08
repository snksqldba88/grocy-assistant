from grocy.api import grocy_get


# ============================================================
# Grocy locations
# ============================================================

def get_locations():
    """
    Return active Grocy locations indexed by lowercase name.
    """

    locations = grocy_get(
        "/api/objects/locations"
    )

    result = {}

    for location in locations:
        name = location.get("name", "").strip()

        if name and location.get("active", 1):
            result[name.lower()] = location

    return result


def find_location(location_name):
    """
    Find a Grocy location by exact or partial name.
    """

    locations = get_locations()

    name = location_name.strip().lower()

    # Exact match
    if name in locations:
        return locations[name]

    # Partial match
    matches = []

    for location_name_key, location in locations.items():
        if name in location_name_key:
            matches.append(location)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        names = ", ".join(
            location["name"]
            for location in matches
        )

        raise ValueError(
            f"Multiple locations match "
            f"'{location_name}': {names}"
        )

    return None