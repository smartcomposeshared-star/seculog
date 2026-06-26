create table login_events (
  id uuid primary key default gen_random_uuid(),
  username text not null,
  ip_address text not null,
  success boolean not null,
  country text,
  lat double precision,
  lon double precision,
  "timestamp" timestamptz not null
);

create table alerts (
  id uuid primary key default gen_random_uuid(),
  login_event_id uuid not null references login_events(id),
  rule_type text not null,
  severity text not null,
  details text not null,
  "timestamp" timestamptz not null
);

alter table alerts add column username text not null default '';

create index idx_alerts_username_rule on alerts (rule_type, timestamp);
create index idx_login_events_username on login_events (username, timestamp);
