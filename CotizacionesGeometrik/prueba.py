from pypvwatts import PVWatts


def coordenadas(lat, lon):
    api_key ='mVIsZR9LB1SmgmI23BUtBFLc4fumDgWwsT2uKLhb'

    PVWatts.api_key = api_key
    result = PVWatts.request(
            system_capacity=1, module_type=1, array_type=1,
            azimuth=180, tilt=10,
            losses=14.08 , lat=lat, lon=lon)
    return result