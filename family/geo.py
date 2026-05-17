def parse_coord(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_coords(data):
    lat = parse_coord(data.get("latitude"))
    lng = parse_coord(data.get("longitude"))
    if lat is None or lng is None:
        return None, None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, None
    return lat, lng


def coord_to_json(value):
    if value is None:
        return None
    return float(value)


def apply_coords(instance, data):
    if "latitude" not in data and "longitude" not in data:
        return
    lat, lng = parse_coords(data)
    instance.latitude = lat
    instance.longitude = lng
