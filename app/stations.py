from app.models import Station


def match_stations(stations: list[Station], query: str) -> list[Station]:
    normalized_query = query.casefold()
    matches: list[Station] = []

    for station in stations:
        names = [station.name, station.standard_name]
        if any(
            normalized_query in name.casefold()
            for name in names
            if name is not None
        ):
            matches.append(station)

    return matches

