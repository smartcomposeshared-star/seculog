from unittest.mock import patch, MagicMock
import requests
from engine.enrichment import geolocate_ip, check_ip_reputation, fetch_blacklisted_ip


@patch("engine.enrichment.requests.get")
def test_geolocate_ip_returns_country_and_coordinates(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "status": "success", "country": "Singapore", "lat": 1.35, "lon": 103.82,
    })
    country, lat, lon = geolocate_ip("1.2.3.4", cache={})
    assert country == "Singapore"
    assert lat == 1.35
    assert lon == 103.82


@patch("engine.enrichment.requests.get")
def test_geolocate_ip_uses_cache_on_second_call(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "status": "success", "country": "Singapore", "lat": 1.35, "lon": 103.82,
    })
    cache = {}
    geolocate_ip("1.2.3.4", cache)
    geolocate_ip("1.2.3.4", cache)
    assert mock_get.call_count == 1


@patch("engine.enrichment.requests.get")
def test_geolocate_ip_handles_failed_lookup(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {"status": "fail"})
    country, lat, lon = geolocate_ip("0.0.0.0", cache={})
    assert country is None and lat is None and lon is None


@patch("engine.enrichment.requests.get")
def test_check_ip_reputation_returns_score(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "data": {"abuseConfidenceScore": 87},
    })
    score = check_ip_reputation("9.9.9.9", api_key="fake", cache={})
    assert score == 87.0


@patch("engine.enrichment.requests.get")
def test_check_ip_reputation_defaults_to_zero_on_error(mock_get):
    mock_get.side_effect = requests.RequestException("network down")
    score = check_ip_reputation("9.9.9.9", api_key="fake", cache={})
    assert score == 0.0


@patch("engine.enrichment.requests.get")
def test_fetch_blacklisted_ip_returns_an_ip_from_the_list(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "data": [{"ipAddress": "203.0.113.200"}],
    })
    ip = fetch_blacklisted_ip(api_key="fake")
    assert ip == "203.0.113.200"


@patch("engine.enrichment.requests.get")
def test_fetch_blacklisted_ip_falls_back_on_error(mock_get):
    mock_get.side_effect = requests.RequestException("network down")
    ip = fetch_blacklisted_ip(api_key="fake", fallback_ip="1.1.1.1")
    assert ip == "1.1.1.1"
