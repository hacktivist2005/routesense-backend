# from flask import Blueprint, jsonify, request

# from services.dns_service import resolve_dns
# from services.ping_service import ping_host
# from services.traceroute_service import traceroute_host
# from services.analysis_service import analyze_network
# from services.diagnostics_service import analyze_diagnostics

# analyzer_bp = Blueprint(
#     "analyzer",
#     __name__,
#     url_prefix="/api",
# )


# @analyzer_bp.route("/analyze", methods=["POST"])
# def analyze():

#     data = request.get_json(silent=True)

#     if not data:
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "Request body is required.",
#             }
#         ), 400

#     target = data.get("target")

#     if not target or not isinstance(target, str):
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "A valid target is required.",
#             }
#         ), 400

#     target = target.strip()

#     if not target:
#         return jsonify(
#             {
#                 "success": False,
#                 "error": "Target cannot be empty.",
#             }
#         ), 400

#     # -----------------------------
#     # DNS
#     # -----------------------------

#     dns_result = resolve_dns(target)

#     if not dns_result["success"]:
#         return jsonify(
#             {
#                 "success": False,
#                 "target": target,
#                 "error": dns_result["error"],
#             }
#         ), 400

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
#     # Intelligence
#     # -----------------------------

#     analysis_result = analyze_network(
#         ping_result,
#         traceroute_result,
#     )

#     diagnostics_result = analyze_diagnostics(
#         ping_result,
#         traceroute_result,
#     )

#     return jsonify(
#     {
#         "success": True,

#         "target": target,

#         "dns": dns_result,

#         "ping": ping_result,

#         "traceroute": traceroute_result,

#         "analysis": analysis_result,

#         "diagnostics": diagnostics_result,
#     }
# )

import asyncio
from flask import Blueprint, jsonify, request

from services.dns_service import resolve_dns
from services.ping_service import ping_host
from services.traceroute_service import traceroute_host
from services.analysis_service import analyze_network
from services.diagnostics_service import analyze_diagnostics

analyzer_bp = Blueprint("analyzer", __name__, url_prefix="/api")

async def process_analysis(target: str):
    # 1. DNS Resolution
    dns_result = await resolve_dns(target)
    if not dns_result["success"]:
        return {"success": False, "target": target, "error": dns_result["error"]}

    resolved_ip = dns_result["ip_address"]

    # 2. Parallel Execution of Ping & Traceroute
    ping_result, traceroute_result = await asyncio.gather(
        ping_host(resolved_ip),
        traceroute_host(resolved_ip)
    )

    # 3. Intelligence Aggregation
    analysis_result = analyze_network(ping_result, traceroute_result)
    diagnostics_result = analyze_diagnostics(ping_result, traceroute_result)

    return {
        "success": True,
        "target": target,
        "dns": dns_result,
        "ping": ping_result,
        "traceroute": traceroute_result,
        "analysis": analysis_result,
        "diagnostics": diagnostics_result,
    }

@analyzer_bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    if not data or not data.get("target") or not isinstance(data.get("target"), str):
        return jsonify({"success": False, "error": "A valid target string is required."}), 400

    target = data.get("target").strip()
    if not target:
        return jsonify({"success": False, "error": "Target cannot be empty."}), 400

    # Run async pipeline synchronously for standard REST route
    result = asyncio.run(process_analysis(target))
    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)