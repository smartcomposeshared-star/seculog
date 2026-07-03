export interface LoginEvent {
  id: string;
  username: string;
  ip_address: string;
  country: string | null;
  lat: number | null;
  lon: number | null;
  success: boolean;
  timestamp: string;
}

export interface Alert {
  id: string;
  login_event_id: string;
  rule_type: "brute_force" | "impossible_travel" | "known_bad_ip";
  severity: "low" | "medium" | "high";
  details: string;
  timestamp: string;
  username: string;
  login_events?: { ip_address: string };
}

export interface MapLocation {
  lat: number;
  lon: number;
  username: string;
  country: string | null;
  suspicious: boolean;
}
