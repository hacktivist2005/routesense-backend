# import platform
# import subprocess
# import re


# def traceroute_host(host):

#     system = platform.system().lower()

#     if system == "windows":
#         command = [
#             "tracert",
#             "-d",
#             "-h",
#             "20",
#             "-w",
#             "500",
#             host,
#         ]
#     else:
#         command = [
#             "traceroute",
#             "-n",
#             "-m",
#             "30",
#             host,
#         ]

#     try:

#         result = subprocess.run(
#             command,
#             capture_output=True,
#             text=True,
#             timeout=30,
#             encoding="utf-8",
#             errors="replace",
#         )

#         # Windows tracert can sometimes write useful
#         # information to stderr, so combine both.
#         output = result.stdout + "\n" + result.stderr

#         hops = []

#         for line in output.splitlines():

#             line = line.strip()

#             if not line:
#                 continue

#             # -----------------------------------------
#             # Extract hop number
#             # -----------------------------------------

#             hop_match = re.match(
#                 r"^(\d+)\s+(.*)$",
#                 line,
#             )

#             if not hop_match:
#                 continue

#             hop_number = int(hop_match.group(1))
#             hop_data = hop_match.group(2)

#             # -----------------------------------------
#             # Extract IPv4 addresses
#             # -----------------------------------------

#             ip_matches = re.findall(
#                 r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
#                 hop_data,
#             )

#             # -----------------------------------------
#             # Extract latency values
#             # -----------------------------------------

#             latency_matches = re.findall(
#                 r"(\d+(?:\.\d+)?)\s*ms",
#                 hop_data,
#             )

#             latencies = [
#                 float(value)
#                 for value in latency_matches
#             ]

#             # -----------------------------------------
#             # TIMEOUT
#             # -----------------------------------------

#             if not ip_matches:

#                 hops.append(
#                     {
#                         "hop": hop_number,
#                         "ip_address": None,
#                         "latency": None,
#                         "status": "timeout",
#                     }
#                 )

#                 continue

#             # -----------------------------------------
#             # SUCCESSFUL HOP
#             # -----------------------------------------

#             ip_address = ip_matches[-1]

#             average_latency = None

#             if latencies:

#                 average_latency = round(
#                     sum(latencies) / len(latencies),
#                     2,
#                 )

#             hop = {
#                 "hop": hop_number,
#                 "ip_address": ip_address,
#                 "latency": average_latency,
#                 "status": "success",
#             }

#             hops.append(hop)

#             # -----------------------------------------
#             # DESTINATION DETECTION
#             # -----------------------------------------
#             #
#             # If this hop matches the resolved target IP,
#             # stop processing further timeout lines.
#             #

#             if ip_address == host:
#                 break

#         # ---------------------------------------------
#         # Remove impossible trailing hops
#         # ---------------------------------------------
#         #
#         # Sometimes traceroute output can contain
#         # extra lines after destination detection.
#         #

#         if hops:

#             destination_index = None

#             for index, hop in enumerate(hops):

#                 if hop["ip_address"] == host:

#                     destination_index = index
#                     break

#             if destination_index is not None:

#                 hops = hops[:destination_index + 1]

#         # ---------------------------------------------
#         # Determine success
#         # ---------------------------------------------

#         destination_reached = any(
#             hop["ip_address"] == host
#             and hop["status"] == "success"
#             for hop in hops
#         )

#         return {
#             "success": destination_reached,
#             "hop_count": len(hops),
#             "hops": hops,
#             "raw_output": output,
#             "return_code": result.returncode,
#             "error": (
#                 None
#                 if destination_reached
#                 else "Destination was not reached."
#             ),
#         }

#     except FileNotFoundError:

#         return {
#             "success": False,
#             "hop_count": 0,
#             "hops": [],
#             "raw_output": "",
#             "return_code": None,
#             "error": "Traceroute utility was not found.",
#         }

#     except subprocess.TimeoutExpired as e:

#         partial_output = ""

#         if e.stdout:
#             partial_output += str(e.stdout)

#         if e.stderr:
#             partial_output += "\n" + str(e.stderr)

#         return {
#             "success": False,
#             "hop_count": 0,
#             "hops": [],
#             "raw_output": partial_output,
#             "return_code": None,
#             "error": "Traceroute operation timed out.",
#         }

#     except Exception as e:

#         return {
#             "success": False,
#             "hop_count": 0,
#             "hops": [],
#             "raw_output": "",
#             "return_code": None,
#             "error": str(e),
#         }

import asyncio
import platform
import re
from typing import Dict, Any

async def traceroute_host(host: str, max_hops: int = 30) -> Dict[str, Any]:
    """
    Asynchronously discovers route paths, hop latency, and destination reachability.
    """
    system = platform.system().lower()

    if system == "windows":
        command = ["tracert", "-d", "-h", str(max_hops), "-w", "500", host]
    else:
        command = ["traceroute", "-n", "-m", str(max_hops), "-w", "1", host]

    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=35.0)
        except asyncio.TimeoutError:
            proc.kill()
            return {
                "success": False,
                "hop_count": 0,
                "hops": [],
                "raw_output": "Execution timed out",
                "return_code": -1,
                "error": "Traceroute operation timed out.",
            }

        output = stdout.decode("utf-8", errors="replace") + "\n" + stderr.decode("utf-8", errors="replace")
        hops = []

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            hop_match = re.match(r"^(\d+)\s+(.*)$", line)
            if not hop_match:
                continue

            hop_number = int(hop_match.group(1))
            hop_data = hop_match.group(2)

            ip_matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", hop_data)
            latency_matches = re.findall(r"(\d+(?:\.\d+)?)\s*ms", hop_data)
            latencies = [float(val) for val in latency_matches]

            if not ip_matches:
                hops.append({
                    "hop": hop_number,
                    "ip_address": None,
                    "latency": None,
                    "status": "timeout",
                })
                continue

            ip_address = ip_matches[-1]
            avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

            hops.append({
                "hop": hop_number,
                "ip_address": ip_address,
                "latency": avg_latency,
                "status": "success",
            })

            if ip_address == host:
                break

        destination_reached = any(
            h["ip_address"] == host and h["status"] == "success" for h in hops
        )

        return {
            "success": destination_reached,
            "hop_count": len(hops),
            "hops": hops,
            "raw_output": output,
            "return_code": proc.returncode,
            "error": None if destination_reached else "Destination hop not reached or ICMP filtered.",
        }

    except Exception as e:
        return {
            "success": False,
            "hop_count": 0,
            "hops": [],
            "raw_output": "",
            "return_code": -1,
            "error": str(e),
        }