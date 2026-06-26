import requests

GEO_API_URL = "http://ip-api.com/json/{ip}"
ABUSEIPDB_CHECK_URL = "https://api.abuseipdb.com/api/v2/check"
ABUSEIPDB_BLACKLIST_URL = "https://api.abuseipdb.com/api/v2/blacklist"


def geolocate_ip(ip_address, cache):
    if ip_address in cache:
        return cache[ip_address]
    try:
        data = requests.get(GEO_API_URL.format(ip=ip_address), timeout=5).json()
        if data.get("status") == "success":
            result = (data.get("country"), data.get("lat"), data.get("lon"))
        else:
            result = (None, None, None)
    except requests.RequestException:
        result = (None, None, None)
    cache[ip_address] = result
    return result


def check_ip_reputation(ip_address, api_key, cache):
    if ip_address in cache:
        return cache[ip_address]
    try:
        data = requests.get(
            ABUSEIPDB_CHECK_URL,
            params={"ipAddress": ip_address, "maxAgeInDays": 90},
            headers={"Key": api_key, "Accept": "application/json"},
            timeout=5,
        ).json()
        score = float(data["data"]["abuseConfidenceScore"])
    except (requests.RequestException, KeyError, ValueError, TypeError):
        score = 0.0
    cache[ip_address] = score
    return score


def fetch_blacklisted_ip(api_key, fallback_ip="185.220.101.1"):
    try:
        data = requests.get(
            ABUSEIPDB_BLACKLIST_URL,
            params={"confidenceMinimum": 90, "limit": 1},
            headers={"Key": api_key, "Accept": "application/json"},
            timeout=5,
        ).json()
        return data["data"][0]["ipAddress"]
    except (requests.RequestException, KeyError, IndexError, TypeError):
        return fallback_ip
