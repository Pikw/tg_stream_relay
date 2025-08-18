from prometheus_client import Counter, Gauge, Histogram

commands_total = Counter("bot_commands_total", "Total commands", ["command"])
relays_started = Counter("relays_started_total", "Total number of relays started")
relays_failed = Counter("relays_failed_total", "Total number of relays failed")
relays_active = Gauge("relays_active", "Currently active relays")
relay_duration = Histogram("relay_duration_seconds", "Relay session durations (s)")
errors_total = Counter("errors_total", "Total errors", ["service"])
