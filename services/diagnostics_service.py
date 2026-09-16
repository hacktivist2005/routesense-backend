# def analyze_diagnostics(ping_data, traceroute_data):
#     """
#     Generate high-level network diagnostics
#     from ping and traceroute results.
#     """

#     diagnostics = []

#     hops = traceroute_data.get("hops", [])

#     packet_loss = ping_data.get("packet_loss") or 0
#     latency = ping_data.get("average_latency")

#     ping_success = ping_data.get("success", False)
#     traceroute_success = traceroute_data.get("success", False)

#     # -----------------------------------------
#     # Destination Reachability
#     # -----------------------------------------

#     destination_reachable = False

#     if hops:
#         last_hop = hops[-1]

#         if (
#             last_hop.get("status") == "success"
#             and last_hop.get("ip_address")
#         ):
#             destination_reachable = traceroute_success

#     if destination_reachable:

#         diagnostics.append({
#             "type": "success",
#             "severity": "low",
#             "title": "Destination Reachable",
#             "message":
#                 "The target endpoint responded successfully "
#                 "during network analysis."
#         })

#     else:

#         diagnostics.append({
#             "type": "critical",
#             "severity": "high",
#             "title": "Destination Unreachable",
#             "message":
#                 "The target endpoint could not be reached "
#                 "during network analysis."
#         })

#     # -----------------------------------------
#     # Packet Loss
#     # -----------------------------------------

#     if packet_loss == 0:

#         diagnostics.append({
#             "type": "success",
#             "severity": "low",
#             "title": "No Packet Loss",
#             "message":
#                 "Connectivity testing detected no packet loss."
#         })

#     elif packet_loss < 25:

#         diagnostics.append({
#             "type": "warning",
#             "severity": "medium",
#             "title": "Packet Loss Detected",
#             "message":
#                 f"Network testing detected {packet_loss}% packet loss."
#         })

#     else:

#         diagnostics.append({
#             "type": "critical",
#             "severity": "high",
#             "title": "High Packet Loss",
#             "message":
#                 f"High packet loss detected: {packet_loss}%."
#         })

#     # -----------------------------------------
#     # Latency
#     # -----------------------------------------

#     if latency is not None:

#         if latency <= 50:

#             diagnostics.append({
#                 "type": "success",
#                 "severity": "low",
#                 "title": "Healthy Latency",
#                 "message":
#                     f"Average latency is {latency} ms, "
#                     "which is within a healthy range."
#             })

#         elif latency <= 100:

#             diagnostics.append({
#                 "type": "warning",
#                 "severity": "medium",
#                 "title": "Moderate Latency",
#                 "message":
#                     f"Average latency is {latency} ms."
#             })

#         else:

#             diagnostics.append({
#                 "type": "critical",
#                 "severity": "high",
#                 "title": "High Latency",
#                 "message":
#                     f"Average latency is {latency} ms, "
#                     "which may indicate network performance issues."
#             })

#     # -----------------------------------------
#     # Timeout Analysis
#     # -----------------------------------------

#     timeout_hops = [
#         hop["hop"]
#         for hop in hops
#         if hop.get("status") == "timeout"
#     ]

#     responsive_after_timeout = False

#     if timeout_hops:

#         last_timeout = max(timeout_hops)

#         for hop in hops:

#             if (
#                 hop["hop"] > last_timeout
#                 and hop.get("status") == "success"
#             ):
#                 responsive_after_timeout = True
#                 break

#         if responsive_after_timeout:

#             diagnostics.append({
#                 "type": "info",
#                 "severity": "low",
#                 "title": "Intermediate ICMP Filtering",
#                 "message":
#                     "Some intermediate hops did not respond, "
#                     "but later hops remained reachable. "
#                     "This behavior may be caused by ICMP filtering "
#                     "or rate limiting."
#             })

#         else:

#             diagnostics.append({
#                 "type": "warning",
#                 "severity": "medium",
#                 "title": "Route Timeout",
#                 "message":
#                     "Timeouts were detected near the end "
#                     "of the discovered route."
#             })

#     # -----------------------------------------
#     # Route Status
#     # -----------------------------------------

#     if destination_reachable and packet_loss == 0:
#         status = "healthy"
#         summary = (
#             "Network appears healthy. "
#             "The destination was confirmed by traceroute "
#             "with no detected packet loss."
#         )

#     elif destination_reachable:
#         status = "degraded"
#         summary = (
#             "The destination was confirmed by traceroute, "
#             "but network conditions show some performance degradation."
#         )

#     else:
#         status = "degraded"
#         summary = (
#             "The destination was not confirmed by traceroute. "
#             "Some intermediate hops may be filtering or "
#             "dropping traceroute probes, while connectivity "
#             "may still be available."
#         )

#     return {
#         "status": status,
#         "summary": summary,
#         "destination_reachable": destination_reachable,
#         "packet_loss": packet_loss,
#         "average_latency": latency,
#         "timeout_hops": timeout_hops,
#         "diagnostics": diagnostics
#     }

from typing import Dict, Any, List

def analyze_diagnostics(ping_data: Dict[str, Any], traceroute_data: Dict[str, Any]) -> Dict[str, Any]:
    diagnostics: List[Dict[str, Any]] = []
    hops = traceroute_data.get("hops", [])
    packet_loss = ping_data.get("packet_loss") or 0.0
    latency = ping_data.get("average_latency")
    dest_reachable = traceroute_data.get("success", False)

    # Reachability
    if dest_reachable:
        diagnostics.append({
            "type": "success", "severity": "low", "title": "Destination Reachable",
            "message": "Target responded continuously over discovered network hops."
        })
    else:
        diagnostics.append({
            "type": "critical", "severity": "high", "title": "Destination Unreachable",
            "message": "Target endpoint could not complete ICMP handshake/traceroute sequence."
        })

    # Loss checks
    if packet_loss > 0:
        sev = "medium" if packet_loss < 20 else "high"
        diagnostics.append({
            "type": "warning" if packet_loss < 20 else "critical",
            "severity": sev,
            "title": f"Packet Loss ({packet_loss}%)",
            "message": "Intermediate node congestion or link loss observed."
        })

    # Latency Check
    if latency and latency > 100:
        diagnostics.append({
            "type": "warning", "severity": "medium", "title": "High Round-Trip Latency",
            "message": f"Average latency is {latency} ms, exceeding optimal engineering thresholds."
        })

    status = "healthy" if dest_reachable and packet_loss == 0 else "degraded"
    summary = "Network route fully functional." if status == "healthy" else "Route degrades near target edge."

    return {
        "status": status,
        "summary": summary,
        "destination_reachable": dest_reachable,
        "packet_loss": packet_loss,
        "average_latency": latency,
        "diagnostics": diagnostics
    }