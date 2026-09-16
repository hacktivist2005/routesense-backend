from services.dns_service import resolve_dns
from services.traceroute_service import traceroute_host


target = "google.com"

# -----------------------------------------
# DNS Resolution
# -----------------------------------------

dns_result = resolve_dns(target)

print("\n==============================")
print("TARGET:", target)
print("==============================")

if not dns_result["success"]:

    print("DNS RESOLUTION FAILED")
    print("ERROR:", dns_result["error"])

    exit()


resolved_ip = dns_result["ip_address"]

print("RESOLVED IP:", resolved_ip)

# -----------------------------------------
# Traceroute
# -----------------------------------------

result = traceroute_host(resolved_ip)

print("\n==============================")

print("TRACEROUTE SUCCESS:", result["success"])

print("HOP COUNT:", result["hop_count"])

print("ERROR:", result["error"])

print("==============================")

print("\nRAW OUTPUT:")

print(result["raw_output"])

print("\nHOPS:")

for hop in result["hops"]:

    print(hop)