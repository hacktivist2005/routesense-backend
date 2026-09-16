# from flask import Blueprint, jsonify, request

# from services.dns_service import resolve_dns
# from services.ping_service import ping_host
# from services.traceroute_service import traceroute_host
# from services.analysis_service import analyze_network


# comparison_bp = Blueprint(
#     "comparison",
#     __name__,
#     url_prefix="/api",
# )


# def analyze_target(target):
#     """
#     Perform complete network analysis for a single target.
#     """

#     target = target.strip()

#     # -----------------------------
#     # DNS
#     # -----------------------------

#     dns_result = resolve_dns(target)

#     if not dns_result["success"]:
#         return {
#             "success": False,
#             "target": target,
#             "error": dns_result["error"],
#         }

#     resolved_ip = dns_result["ip_address"]

#     # -----------------------------
#     # Ping
#     # -----------------------------

#     ping_result = ping_host(resolved_ip)

#     # -----------------------------
#     # Traceroute
#     # -----------------------------

#     traceroute_result = traceroute_host(resolved_ip)

#     # -----------------------------
#     # Network Analysis
#     # -----------------------------

#     analysis_result = analyze_network(
#         ping_result,
#         traceroute_result,
#     )

#     return {
#         "success": True,
#         "target": target,
#         "dns": dns_result,
#         "ping": ping_result,
#         "traceroute": traceroute_result,
#         "analysis": analysis_result,
#     }


# @comparison_bp.route("/compare", methods=["POST"])
# def compare():

#     data = request.get_json(silent=True)

#     # -----------------------------
#     # Validate request
#     # -----------------------------

#     if not data:
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "Request body is required.",
#             }
#         ), 400

#     target_a = data.get("target_a")
#     target_b = data.get("target_b")

#     if not target_a or not isinstance(target_a, str):
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "A valid Target A is required.",
#             }
#         ), 400

#     if not target_b or not isinstance(target_b, str):
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "A valid Target B is required.",
#             }
#         ), 400

#     target_a = target_a.strip()
#     target_b = target_b.strip()

#     if not target_a or not target_b:
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "Both targets are required.",
#             }
#         ), 400

#     # -----------------------------
#     # Analyze Target A
#     # -----------------------------

#     result_a = analyze_target(target_a)

#     if not result_a["success"]:
#         return jsonify(
#             {
#                 "success": False,
#                 "target": target_a,
#                 "error": result_a["error"],
#             }
#         ), 400

#     # -----------------------------
#     # Analyze Target B
#     # -----------------------------

#     result_b = analyze_target(target_b)

#     if not result_b["success"]:
#         return jsonify(
#             {
#                 "success": False,
#                 "target": target_b,
#                 "error": result_b["error"],
#             }
#         ), 400

#     # -----------------------------
#     # Extract metrics
#     # -----------------------------

#     health_a = result_a["analysis"]["health_metrics"]
#     health_b = result_b["analysis"]["health_metrics"]

#     latency_a = result_a["ping"].get(
#         "average_latency"
#     )

#     latency_b = result_b["ping"].get(
#         "average_latency"
#     )

#     packet_loss_a = result_a["ping"].get(
#         "packet_loss"
#     )

#     packet_loss_b = result_b["ping"].get(
#         "packet_loss"
#     )

#     hops_a = result_a["traceroute"].get(
#         "hop_count",
#         len(result_a["traceroute"].get("hops", [])),
#     )

#     hops_b = result_b["traceroute"].get(
#         "hop_count",
#         len(result_b["traceroute"].get("hops", [])),
#     )

#     # -----------------------------
#     # Route Difference
#     # -----------------------------

#     route_a = result_a["traceroute"].get(
#         "hops",
#         []
#     )

#     route_b = result_b["traceroute"].get(
#         "hops",
#         []
#     )

#     max_positions = max(
#         len(route_a),
#         len(route_b),
#     )

#     different_positions = 0

#     for index in range(max_positions):

#         ip_a = (
#             route_a[index].get("ip_address")
#             if index < len(route_a)
#             else None
#         )

#         ip_b = (
#             route_b[index].get("ip_address")
#             if index < len(route_b)
#             else None
#         )

#         if ip_a != ip_b:
#             different_positions += 1

#     # -----------------------------
#     # Performance comparison
#     # -----------------------------

#     latency_difference = None

#     if latency_a is not None and latency_b is not None:
#         latency_difference = round(
#             abs(latency_a - latency_b),
#             2,
#         )

#     hop_difference = abs(
#         hops_a - hops_b
#     )

#     health_difference = abs(
#         health_a["overall"]
#         - health_b["overall"]
#     )

#     # -----------------------------
#     # Determine better route
#     # -----------------------------

#     score_a = 0
#     score_b = 0

#     if latency_a is not None and latency_b is not None:

#         if latency_a < latency_b:
#             score_a += 1

#         elif latency_b < latency_a:
#             score_b += 1

#     if packet_loss_a is not None and packet_loss_b is not None:

#         if packet_loss_a < packet_loss_b:
#             score_a += 1

#         elif packet_loss_b < packet_loss_a:
#             score_b += 1

#     if health_a["overall"] > health_b["overall"]:
#         score_a += 1

#     elif health_b["overall"] > health_a["overall"]:
#         score_b += 1

#     if score_a > score_b:
#         better_target = target_a

#     elif score_b > score_a:
#         better_target = target_b

#     else:
#         better_target = "Tie"

#     # -----------------------------
#     # Final comparison response
#     # -----------------------------

#     return jsonify(
#         {
#             "success": True,

#             "target_a": {
#                 "target": target_a,
#                 "dns": result_a["dns"],
#                 "latency": latency_a,
#                 "packet_loss": packet_loss_a,
#                 "hops": hops_a,
#                 "health": health_a["overall"],
#                 "health_metrics": health_a,
#             },

#             "target_b": {
#                 "target": target_b,
#                 "dns": result_b["dns"],
#                 "latency": latency_b,
#                 "packet_loss": packet_loss_b,
#                 "hops": hops_b,
#                 "health": health_b["overall"],
#                 "health_metrics": health_b,
#             },

#             "comparison": {
#                 "latency_difference": latency_difference,
#                 "hop_difference": hop_difference,
#                 "health_difference": health_difference,
#                 "different_route_positions": different_positions,
#                 "better_target": better_target,
#             },
#         }
#     )

import asyncio
from flask import Blueprint, jsonify, request

from services.dns_service import resolve_dns
from services.ping_service import ping_host
from services.traceroute_service import traceroute_host
from services.analysis_service import analyze_network

comparison_bp = Blueprint("comparison", __name__, url_prefix="/api")

async def analyze_target_async(target: str):
    dns_result = await resolve_dns(target.strip())
    if not dns_result["success"]:
        return {"success": False, "target": target, "error": dns_result["error"]}

    resolved_ip = dns_result["ip_address"]

    # Concurrent execution for instant feedback
    ping_result, traceroute_result = await asyncio.gather(
        ping_host(resolved_ip),
        traceroute_host(resolved_ip)
    )

    analysis_result = analyze_network(ping_result, traceroute_result)

    return {
        "success": True,
        "target": target,
        "dns": dns_result,
        "ping": ping_result,
        "traceroute": traceroute_result,
        "analysis": analysis_result,
    }

@comparison_bp.route("/compare", methods=["POST"])
def compare():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Request body is required."}), 400

    target_a = data.get("target_a")
    target_b = data.get("target_b")

    if not target_a or not isinstance(target_a, str) or not target_b or not isinstance(target_b, str):
        return jsonify({"success": False, "error": "Both target_a and target_b are required."}), 400

    target_a = target_a.strip()
    target_b = target_b.strip()

    if not target_a or not target_b:
        return jsonify({"success": False, "error": "Targets cannot be empty."}), 400

    # PARALLEL PIPELINE: Both Target A and Target B process at the same time!
    async def run_parallel_comparison():
        return await asyncio.gather(
            analyze_target_async(target_a),
            analyze_target_async(target_b)
        )

    result_a, result_b = asyncio.run(run_parallel_comparison())

    if not result_a["success"]:
        return jsonify({"success": False, "target": target_a, "error": f"Target A: {result_a['error']}"}), 400

    if not result_b["success"]:
        return jsonify({"success": False, "target": target_b, "error": f"Target B: {result_b['error']}"}), 400

    # Metrics Extraction
    health_a = result_a["analysis"]["health_metrics"]
    health_b = result_b["analysis"]["health_metrics"]

    latency_a = result_a["ping"].get("average_latency")
    latency_b = result_b["ping"].get("average_latency")

    loss_a = result_a["ping"].get("packet_loss")
    loss_b = result_b["ping"].get("packet_loss")

    hops_a = result_a["traceroute"].get("hop_count", 0)
    hops_b = result_b["traceroute"].get("hop_count", 0)

    # Route Positional Divergence Calculation
    route_a = result_a["traceroute"].get("hops", [])
    route_b = result_b["traceroute"].get("hops", [])
    max_len = max(len(route_a), len(route_b))
    divergent_hops = 0

    for i in range(max_len):
        ip_a = route_a[i].get("ip_address") if i < len(route_a) else None
        ip_b = route_b[i].get("ip_address") if i < len(route_b) else None
        if ip_a != ip_b:
            divergent_hops += 1

    # Route Superiority Scoring Algorithm
    score_a, score_b = 0, 0
    if latency_a is not None and latency_b is not None:
        if latency_a < latency_b: score_a += 1
        elif latency_b < latency_a: score_b += 1

    if loss_a is not None and loss_b is not None:
        if loss_a < loss_b: score_a += 1
        elif loss_b < loss_a: score_b += 1

    if health_a["overall"] > health_b["overall"]: score_a += 1
    elif health_b["overall"] > health_a["overall"]: score_b += 1

    better_target = target_a if score_a > score_b else (target_b if score_b > score_a else "Tie")

    return jsonify({
        "success": True,
        "target_a": {
            "target": target_a,
            "dns": result_a["dns"],
            "latency": latency_a,
            "packet_loss": loss_a,
            "hops": hops_a,
            "health": health_a["overall"],
            "health_metrics": health_a,
            "raw_analysis": result_a["analysis"]
        },
        "target_b": {
            "target": target_b,
            "dns": result_b["dns"],
            "latency": latency_b,
            "packet_loss": loss_b,
            "hops": hops_b,
            "health": health_b["overall"],
            "health_metrics": health_b,
            "raw_analysis": result_b["analysis"]
        },
        "comparison": {
            "latency_difference": round(abs(latency_a - latency_b), 2) if latency_a and latency_b else None,
            "hop_difference": abs(hops_a - hops_b),
            "health_difference": abs(health_a["overall"] - health_b["overall"]),
            "different_route_positions": divergent_hops,
            "better_target": better_target,
        }
    })