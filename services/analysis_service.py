# def detect_latency_spikes(hops):
#     """
#     Detect significant latency increases between
#     consecutive responsive hops.
#     """

#     spikes = []

#     previous_latency = None
#     previous_hop = None

#     for hop in hops:

#         latency = hop.get("latency")

#         if latency is None:
#             continue

#         if previous_latency is not None:

#             increase = latency - previous_latency

#             # Significant increase
#             if increase >= 10:

#                 spikes.append(
#                     {
#                         "hop": hop["hop"],
#                         "previous_hop": previous_hop,
#                         "previous_latency": previous_latency,
#                         "latency": latency,
#                         "increase": round(increase, 2),
#                     }
#                 )

#         previous_latency = latency
#         previous_hop = hop["hop"]

#     return spikes


# def analyze_timeouts(hops):
#     """
#     Analyze timeout hops without automatically
#     treating them as network failures.
#     """

#     timeout_hops = []

#     for hop in hops:

#         if hop.get("status") == "timeout":

#             timeout_hops.append(
#                 hop["hop"]
#             )

#     return timeout_hops

# def group_timeout_ranges(hops):
#     """
#     Group consecutive timeout hops into ranges.
#     Example:
#     [4, 10, 11, 12, 13, 14, 15, 16]

#     becomes:

#     [
#         {"start": 4, "end": 4, "count": 1},
#         {"start": 10, "end": 16, "count": 7}
#     ]
#     """

#     timeout_hops = [
#         hop["hop"]
#         for hop in hops
#         if hop.get("status") == "timeout"
#     ]

#     if not timeout_hops:
#         return []

#     ranges = []

#     start = timeout_hops[0]
#     previous = timeout_hops[0]

#     for hop_number in timeout_hops[1:]:

#         if hop_number == previous + 1:
#             previous = hop_number

#         else:

#             ranges.append(
#                 {
#                     "start": start,
#                     "end": previous,
#                     "count": previous - start + 1,
#                 }
#             )

#             start = hop_number
#             previous = hop_number

#     ranges.append(
#         {
#             "start": start,
#             "end": previous,
#             "count": previous - start + 1,
#         }
#     )

#     return ranges

# def generate_route_insights(
#     ping_data,
#     traceroute_data,
# ):

#     insights = []

#     hops = traceroute_data.get("hops", [])

#     # ------------------------------------------------
#     # Packet loss
#     # ------------------------------------------------

#     if ping_data.get("success"):

#         packet_loss = ping_data.get(
#             "packet_loss"
#         ) or 0

#         if packet_loss == 0:

#             insights.append(
#                 {
#                     "type": "success",
#                     "category": "connectivity",
#                     "message":
#                         "No packet loss detected during connectivity testing.",
#                 }
#             )

#         elif packet_loss < 25:

#             insights.append(
#                 {
#                     "type": "warning",
#                     "category": "connectivity",
#                     "message":
#                         f"Packet loss detected: {packet_loss}%.",
#                 }
#             )

#         else:

#             insights.append(
#                 {
#                     "type": "critical",
#                     "category": "connectivity",
#                     "message":
#                         f"High packet loss detected: {packet_loss}%.",
#                 }
#             )

#     # ------------------------------------------------
#     # Average latency
#     # ------------------------------------------------

#     latency = ping_data.get(
#         "average_latency"
#     )

#     if latency is not None:

#         if latency <= 50:

#             insights.append(
#                 {
#                     "type": "success",
#                     "category": "latency",
#                     "message":
#                         f"Average latency is healthy at {latency} ms.",
#                 }
#             )

#         elif latency <= 100:

#             insights.append(
#                 {
#                     "type": "warning",
#                     "category": "latency",
#                     "message":
#                         f"Moderate latency detected at {latency} ms.",
#                 }
#             )

#         else:

#             insights.append(
#                 {
#                     "type": "critical",
#                     "category": "latency",
#                     "message":
#                         f"High average latency detected at {latency} ms.",
#                 }
#             )

#     # ------------------------------------------------
#     # Route hops
#     # ------------------------------------------------

#     if hops:

#         insights.append(
#             {
#                 "type": "info",
#                 "category": "route",
#                 "message":
#                     f"{len(hops)} network hops were discovered.",
#             }
#         )

#     # ------------------------------------------------
#     # Latency spikes
#     # ------------------------------------------------

#     spikes = detect_latency_spikes(hops)

#     for spike in spikes:

#         insights.append(
#             {
#                 "type": "warning",
#                 "category": "latency_spike",
#                 "message":
#                     f"Latency spike detected at Hop "
#                     f"{spike['hop']}: "
#                     f"{spike['previous_latency']} ms → "
#                     f"{spike['latency']} ms "
#                     f"(+{spike['increase']} ms).",
#                 "hop": spike["hop"],
#                 "increase": spike["increase"],
#             }
#         )

#     # ------------------------------------------------
#     # Timeout analysis
#     # ------------------------------------------------

#     timeout_hops = analyze_timeouts(hops)

#     if timeout_hops:

#         responsive_after_timeout = False

#         for hop in hops:

#             if (
#                 hop["hop"] > max(timeout_hops)
#                 and hop["status"] == "success"
#             ):
#                 responsive_after_timeout = True
#                 break

#         if responsive_after_timeout:

#             insights.append(
#                 {
#                     "type": "info",
#                     "category": "timeout",
#                     "message":
#                         "Some intermediate hops did not respond, "
#                         "but subsequent hops remained reachable. "
#                         "This may indicate ICMP filtering or "
#                         "rate limiting rather than a connectivity failure.",
#                     "hops": timeout_hops,
#                 }
#             )

#         else:

#             insights.append(
#                 {
#                     "type": "warning",
#                     "category": "timeout",
#                     "message":
#                         "Timeouts were detected near the end "
#                         "of the route.",
#                     "hops": timeout_hops,
#                 }
#             )

#     return insights

# def analyze_network(
#     ping_data,
#     traceroute_data,
# ):

#     # --------------------------------------------
#     # Health Metrics
#     # --------------------------------------------

#     health_metrics = calculate_health_metrics(
#         ping_data,
#         traceroute_data,
#     )

#     # --------------------------------------------
#     # Timeout Analysis
#     # --------------------------------------------

#     timeout_ranges = group_timeout_ranges(
#         traceroute_data.get("hops", [])
#     )

#     timeout_hops = analyze_timeouts(
#         traceroute_data.get("hops", [])
#     )

#     # --------------------------------------------
#     # Latency Spike Analysis
#     # --------------------------------------------

#     spikes = detect_latency_spikes(
#         traceroute_data.get("hops", [])
#     )

#     # --------------------------------------------
#     # Network Insights
#     # --------------------------------------------

#     insights = generate_route_insights(
#         ping_data,
#         traceroute_data,
#     )

#     performance_metrics = calculate_performance_metrics(
#         ping_data,
#         traceroute_data,
#     )

#     # --------------------------------------------
#     # Final Analysis Result
#     # --------------------------------------------

#     return {

#         "health_score": health_metrics["overall"],

#         "health_metrics": health_metrics,

#         "insights": insights,

#         "latency_spikes": spikes,

#         "timeout_hops": timeout_hops,

#         "timeout_ranges": timeout_ranges,

#         "performance_metrics": performance_metrics,

#     }

# def calculate_connectivity_score(ping_data, traceroute_data):
#     score = 100

#     if not ping_data.get("success"):
#         return 0

#     packet_loss = ping_data.get("packet_loss") or 0

#     score -= min(packet_loss * 2, 70)

#     if not traceroute_data.get("success"):
#         score -= 20

#     return max(0, round(score))


# def calculate_latency_score(ping_data, traceroute_data):
#     latency = ping_data.get("average_latency")

#     if latency is None:
#         return 0

#     if latency <= 20:
#         score = 100

#     elif latency <= 50:
#         score = 95

#     elif latency <= 100:
#         score = 80

#     elif latency <= 150:
#         score = 65

#     elif latency <= 250:
#         score = 45

#     else:
#         score = 25

#     hops = traceroute_data.get("hops", [])

#     spikes = detect_latency_spikes(hops)

#     score -= min(len(spikes) * 5, 20)

#     return max(0, round(score))


# def calculate_route_stability_score(traceroute_data):
#     hops = traceroute_data.get("hops", [])

#     if not hops:
#         return 0

#     timeout_hops = [
#         hop
#         for hop in hops
#         if hop.get("status") == "timeout"
#     ]

#     if not timeout_hops:
#         return 100

#     # -----------------------------------------
#     # Destination reachability
#     # -----------------------------------------

#     destination_reached = (
#         hops[-1].get("status") == "success"
#     )

#     # -----------------------------------------
#     # Count timeouts
#     # -----------------------------------------

#     timeout_count = len(timeout_hops)

#     # -----------------------------------------
#     # Destination reachable:
#     # intermediate ICMP filtering is less
#     # significant than actual route failure.
#     # -----------------------------------------

#     if destination_reached:

#         # Only apply a small penalty for
#         # intermediate non-responsive hops.

#         if timeout_count == 1:
#             score = 98

#         elif timeout_count <= 3:
#             score = 96

#         elif timeout_count <= 6:
#             score = 94

#         else:
#             score = 92

#     else:

#         # Destination not reachable.
#         # Timeouts become much more important.

#         timeout_ratio = timeout_count / len(hops)

#         score = 100 - (
#             timeout_ratio * 70
#         )

#     return max(
#         0,
#         min(
#             100,
#             round(score)
#         )
#     )


# def calculate_health_metrics(
#     ping_data,
#     traceroute_data,
# ):
#     connectivity = calculate_connectivity_score(
#         ping_data,
#         traceroute_data,
#     )

#     latency = calculate_latency_score(
#         ping_data,
#         traceroute_data,
#     )

#     route_stability = calculate_route_stability_score(
#         traceroute_data,
#     )

#     overall = round(
#         connectivity * 0.40
#         + latency * 0.30
#         + route_stability * 0.30
#     )

#     return {
#         "overall": overall,
#         "connectivity": connectivity,
#         "latency": latency,
#         "route_stability": route_stability,
#     }

# def calculate_performance_metrics(
#     ping_data,
#     traceroute_data,
# ):
#     hops = traceroute_data.get("hops", [])

#     responsive_hops = [
#         hop
#         for hop in hops
#         if hop.get("status") == "success"
#         and hop.get("latency") is not None
#     ]

#     timeout_hops = [
#         hop
#         for hop in hops
#         if hop.get("status") == "timeout"
#     ]

#     latencies = [
#         hop["latency"]
#         for hop in responsive_hops
#     ]

#     # --------------------------------------------
#     # Ping latency
#     # --------------------------------------------

#     average_latency = ping_data.get(
#         "average_latency"
#     )

#     # --------------------------------------------
#     # Minimum / Maximum latency
#     # --------------------------------------------

#     minimum_latency = (
#         min(latencies)
#         if latencies
#         else None
#     )

#     maximum_latency = (
#         max(latencies)
#         if latencies
#         else None
#     )

#     # --------------------------------------------
#     # Jitter
#     # Average difference between consecutive hops
#     # --------------------------------------------

#     jitter = 0

#     if len(latencies) > 1:

#         differences = [
#             abs(latencies[i] - latencies[i - 1])
#             for i in range(1, len(latencies))
#         ]

#         jitter = round(
#             sum(differences) / len(differences),
#             2,
#         )

#     # --------------------------------------------
#     # Timeout rate
#     # --------------------------------------------

#     total_hops = len(hops)

#     timeout_rate = 0

#     if total_hops > 0:

#         timeout_rate = round(
#             (len(timeout_hops) / total_hops) * 100,
#             2,
#         )

#     # --------------------------------------------
#     # Worst latency hop
#     # --------------------------------------------

#     worst_latency_hop = None

#     if responsive_hops:

#         worst_hop = max(
#             responsive_hops,
#             key=lambda hop: hop["latency"],
#         )

#         worst_latency_hop = {
#             "hop": worst_hop["hop"],
#             "ip_address": worst_hop.get(
#                 "ip_address"
#             ),
#             "latency": worst_hop["latency"],
#         }

#     # --------------------------------------------
#     # Route reliability
#     # --------------------------------------------

#     route_reliability = 0

#     if total_hops > 0:

#         route_reliability = round(
#             (
#                 len(responsive_hops)
#                 / total_hops
#             ) * 100
#         )

#     return {
#         "average_latency": average_latency,

#         "minimum_latency": (
#             round(minimum_latency, 2)
#             if minimum_latency is not None
#             else None
#         ),

#         "maximum_latency": (
#             round(maximum_latency, 2)
#             if maximum_latency is not None
#             else None
#         ),

#         "jitter": jitter,

#         "responsive_hops": len(
#             responsive_hops
#         ),

#         "timeout_hops": len(
#             timeout_hops
#         ),

#         "timeout_rate": timeout_rate,

#         "worst_latency_hop": worst_latency_hop,

#         "route_reliability": route_reliability,
#     }

import math
from typing import List, Dict, Any

def detect_latency_spikes(hops: List[Dict[str, Any]], threshold_ms: float = 15.0) -> List[Dict[str, Any]]:
    spikes = []
    prev_hop = None

    for hop in hops:
        if hop.get("status") != "success" or hop.get("latency") is None:
            continue
        
        if prev_hop:
            delta = hop["latency"] - prev_hop["latency"]
            if delta >= threshold_ms:
                spikes.append({
                    "hop": hop["hop"],
                    "previous_hop": prev_hop["hop"],
                    "previous_latency": prev_hop["latency"],
                    "latency": hop["latency"],
                    "increase": round(delta, 2),
                })
        prev_hop = hop
    return spikes

def group_timeout_ranges(hops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    timeouts = [h["hop"] for h in hops if h.get("status") == "timeout"]
    if not timeouts:
        return []

    ranges = []
    start = timeouts[0]
    prev = timeouts[0]

    for h in timeouts[1:]:
        if h == prev + 1:
            prev = h
        else:
            ranges.append({"start": start, "end": prev, "count": prev - start + 1})
            start = h
            prev = h
    ranges.append({"start": start, "end": prev, "count": prev - start + 1})
    return ranges

def calculate_performance_metrics(ping_data: Dict[str, Any], traceroute_data: Dict[str, Any]) -> Dict[str, Any]:
    hops = traceroute_data.get("hops", [])
    responsive_hops = [h for h in hops if h.get("status") == "success" and h.get("latency") is not None]
    latencies = [h["latency"] for h in responsive_hops]

    jitter = 0.0
    if len(latencies) > 1:
        diffs = [abs(latencies[i] - latencies[i - 1]) for i in range(1, len(latencies))]
        jitter = round(sum(diffs) / len(diffs), 2)

    total_hops = len(hops)
    timeout_count = total_hops - len(responsive_hops)
    timeout_rate = round((timeout_count / total_hops) * 100, 2) if total_hops > 0 else 0.0

    worst_hop = max(responsive_hops, key=lambda x: x["latency"], default=None)

    return {
        "average_latency": ping_data.get("average_latency"),
        "minimum_latency": min(latencies, default=None),
        "maximum_latency": max(latencies, default=None),
        "jitter": jitter,
        "responsive_hops": len(responsive_hops),
        "timeout_hops": timeout_count,
        "timeout_rate": timeout_rate,
        "worst_latency_hop": {
            "hop": worst_hop["hop"],
            "ip_address": worst_hop.get("ip_address"),
            "latency": worst_hop["latency"],
        } if worst_hop else None,
        "route_reliability": round((len(responsive_hops) / total_hops) * 100) if total_hops > 0 else 0,
    }

def calculate_health_metrics(ping_data: Dict[str, Any], traceroute_data: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Check Ping & Reachability
    ping_success = ping_data.get("success", False)
    loss = ping_data.get("packet_loss") or 0.0
    
    # Target unreachable guard check
    if not ping_success or loss == 100:
        return {
            "overall": 0,
            "connectivity": 0,
            "latency": 0,
            "route_stability": 0,
        }

    # 2. Connectivity Score
    connectivity = max(0, round(100 - (loss * 2)))

    # 3. Latency Score
    avg_lat = ping_data.get("average_latency")
    if avg_lat is None:
        latency_score = 0
    else:
        if avg_lat <= 20: latency_score = 100
        elif avg_lat <= 50: latency_score = 90
        elif avg_lat <= 100: latency_score = 75
        elif avg_lat <= 200: latency_score = 50
        else: latency_score = 25

    # 4. Route Stability Score
    hops = traceroute_data.get("hops", [])
    dest_reached = traceroute_data.get("success", False)
    timeouts = [h for h in hops if h.get("status") == "timeout"]
    
    if not dest_reached or not hops:
        stability = 0
    else:
        stability = max(50, 100 - (len(timeouts) * 5))

    overall = round(connectivity * 0.40 + latency_score * 0.35 + stability * 0.25)
    
    return {
        "overall": overall,
        "connectivity": connectivity,
        "latency": latency_score,
        "route_stability": stability,
    }

def analyze_network(ping_data: Dict[str, Any], traceroute_data: Dict[str, Any]) -> Dict[str, Any]:
    hops = traceroute_data.get("hops", [])
    health_metrics = calculate_health_metrics(ping_data, traceroute_data)
    performance_metrics = calculate_performance_metrics(ping_data, traceroute_data)
    
    return {
        "health_score": health_metrics["overall"],
        "health_metrics": health_metrics,
        "performance_metrics": performance_metrics,
        "latency_spikes": detect_latency_spikes(hops),
        "timeout_ranges": group_timeout_ranges(hops),
    }