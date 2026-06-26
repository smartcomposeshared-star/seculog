from engine.geo import haversine_km


def test_distance_between_singapore_and_moscow_is_about_8400km():
    distance = haversine_km(1.3521, 103.8198, 55.7558, 37.6173)
    assert 8300 < distance < 8500


def test_distance_between_same_point_is_zero():
    distance = haversine_km(1.35, 103.82, 1.35, 103.82)
    assert distance == 0
