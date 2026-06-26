from engine.generator import generate_events
from engine.rules.brute_force import detect_brute_force
from engine.rules.impossible_travel import detect_impossible_travel


def test_generates_expected_total_event_count():
    events = generate_events(num_normal_users=3, seed=42)
    # 3 normal + 6 brute-force attempts + 2 impossible-travel logins + 1 bad-ip login
    assert len(events) == 3 + 6 + 2 + 1


def test_planted_brute_force_scenario_is_detectable():
    events = generate_events(num_normal_users=3, seed=42)
    alerts = detect_brute_force(events)
    assert len(alerts) == 1
    assert alerts[0].login_event.username == "attacker_bf"


def test_planted_impossible_travel_scenario_is_detectable():
    events = generate_events(num_normal_users=3, seed=42)
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 1
    assert alerts[0].login_event.username == "traveler_it"


def test_planted_bad_ip_login_uses_the_given_bad_ip():
    events = generate_events(num_normal_users=3, bad_ip="1.2.3.4", seed=42)
    bad_ip_events = [e for e in events if e.ip_address == "1.2.3.4"]
    assert len(bad_ip_events) == 1
    assert bad_ip_events[0].username == "visitor_bip"
