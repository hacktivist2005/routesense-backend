# # import platform
# # import subprocess
# # import re


# # def ping_host(host):
# #     """
# #     Ping a target and calculate basic latency information.
# #     """

# #     system = platform.system().lower()

# #     if system == "windows":
# #         command = ["ping", "-n", "4", host]
# #     else:
# #         command = ["ping", "-c", "4", host]

# #     try:
# #         result = subprocess.run(
# #             command,
# #             capture_output=True,
# #             text=True,
# #             timeout=15,
# #         )

# #         output = result.stdout

# #         latency_values = []

# #         if system == "windows":
# #             matches = re.findall(r"time[=<]\s*(\d+)\s*ms", output)
# #         else:
# #             matches = re.findall(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", output)

# #         latency_values = [float(value) for value in matches]

# #         if latency_values:
# #             average = round(
# #                 sum(latency_values) / len(latency_values),
# #                 2,
# #             )

# #             minimum = round(min(latency_values), 2)
# #             maximum = round(max(latency_values), 2)

# #         else:
# #             average = None
# #             minimum = None
# #             maximum = None

# #         transmitted = 4
# #         received = len(latency_values)

# #         packet_loss = round(
# #             ((transmitted - received) / transmitted) * 100,
# #             2,
# #         )

# #         return {
# #             "success": received > 0,
# #             "average_latency": average,
# #             "minimum_latency": minimum,
# #             "maximum_latency": maximum,
# #             "packet_loss": packet_loss,
# #             "packets_sent": transmitted,
# #             "packets_received": received,
# #             "raw_output": output,
# #             "error": None if received > 0 else "Host did not respond.",
# #         }

# #     except subprocess.TimeoutExpired:
# #         return {
# #             "success": False,
# #             "average_latency": None,
# #             "minimum_latency": None,
# #             "maximum_latency": None,
# #             "packet_loss": 100,
# #             "packets_sent": 4,
# #             "packets_received": 0,
# #             "raw_output": "",
# #             "error": "Ping request timed out.",
# #         }

# #     except Exception as e:
# #         return {
# #             "success": False,
# #             "average_latency": None,
# #             "minimum_latency": None,
# #             "maximum_latency": None,
# #             "packet_loss": None,
# #             "packets_sent": 4,
# #             "packets_received": 0,
# #             "raw_output": "",
# #             "error": str(e),
# #         }

# import asyncio
# import platform
# import re
# from typing import Dict, Any

# async def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
#     """
#     Asynchronously ping a target host without blocking the main event loop.
#     """
#     system = platform.system().lower()
    
#     if system == "windows":
#         command = ["ping", "-n", str(count), "-w", "1000", host]
#     else:
#         command = ["ping", "-c", str(count), "-W", "1", host]

#     try:
#         proc = await asyncio.create_subprocess_exec(
#             *command,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )
        
#         try:
#             stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
#         except asyncio.TimeoutError:
#             proc.kill()
#             return {
#                 "success": False,
#                 "average_latency": None,
#                 "minimum_latency": None,
#                 "maximum_latency": None,
#                 "packet_loss": 100.0,
#                 "packets_sent": count,
#                 "packets_received": 0,
#                 "raw_output": "",
#                 "error": "Ping operation timed out.",
#             }

#         output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")

#         # Robust cross-platform regex matching
#         matches = re.findall(r"(?:time|tiempo)[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
#         if not matches:
#             # Unix fallback parser logic
#             matches = re.findall(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/", output)
#             if matches:
#                 # Extract min/avg/max directly from Unix ping summary block
#                 min_l, avg_l, max_l = matches[0]
#                 latency_values = [float(avg_l)]
#             else:
#                 latency_values = []
#         else:
#             latency_values = [float(v) for v in matches]

#         received = len(latency_values)
        
#         if received > 0:
#             average = round(sum(latency_values) / received, 2)
#             minimum = round(min(latency_values), 2)
#             maximum = round(max(latency_values), 2)
#             packet_loss = round(((count - received) / count) * 100, 2)
            
#             return {
#                 "success": True,
#                 "average_latency": average,
#                 "minimum_latency": minimum,
#                 "maximum_latency": maximum,
#                 "packet_loss": packet_loss,
#                 "packets_sent": count,
#                 "packets_received": received,
#                 "raw_output": output,
#                 "error": None,
#             }

#         return {
#             "success": False,
#             "average_latency": None,
#             "minimum_latency": None,
#             "maximum_latency": None,
#             "packet_loss": 100.0,
#             "packets_sent": count,
#             "packets_received": 0,
#             "raw_output": output,
#             "error": "Host unreachable / No response.",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "average_latency": None,
#             "minimum_latency": None,
#             "maximum_latency": None,
#             "packet_loss": None,
#             "packets_sent": count,
#             "packets_received": 0,
#             "raw_output": "",
#             "error": str(e),
#         }

import asyncio
import platform
import re
import socket
import time
from typing import Dict, Any

async def tcp_ping_fallback(host: str, port: int = 80, timeout: float = 2.0) -> float:
    loop = asyncio.get_event_loop()
    start_time = time.time()
    try:
        await loop.run_in_executor(
            None,
            lambda: socket.create_connection((host, port), timeout=timeout).close()
        )
        return round((time.time() - start_time) * 1000, 2)
    except Exception:
        return None

async def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
    system = platform.system().lower()
    
    if system == "windows":
        command = ["ping", "-n", str(count), "-w", "1000", host]
    else:
        command = ["ping", "-c", str(count), "-W", "1", host]

    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
        output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")

        matches = re.findall(r"(?:time|tiempo)[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
        if not matches:
            matches = re.findall(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/", output)
            latency_values = [float(matches[0][1])] if matches else []
        else:
            latency_values = [float(v) for v in matches]

        if latency_values:
            received = len(latency_values)
            return {
                "success": True,
                "average_latency": round(sum(latency_values) / received, 2),
                "minimum_latency": round(min(latency_values), 2),
                "maximum_latency": round(max(latency_values), 2),
                "packet_loss": round(((count - received) / count) * 100, 2),
                "packets_sent": count,
                "packets_received": received,
                "raw_output": output,
                "error": None,
            }
    except Exception:
        pass

    # --- CLOUD FALLBACK (When ICMP CLI ping fails on Render) ---
    latencies = []
    for _ in range(count):
        lat = await tcp_ping_fallback(host, port=80)
        if lat is None:
            lat = await tcp_ping_fallback(host, port=443)
        if lat is not None:
            latencies.append(lat)
        await asyncio.sleep(0.1)

    if latencies:
        received = len(latencies)
        return {
            "success": True,
            "average_latency": round(sum(latencies) / received, 2),
            "minimum_latency": round(min(latencies), 2),
            "maximum_latency": round(max(latencies), 2),
            "packet_loss": round(((count - received) / count) * 100, 2),
            "packets_sent": count,
            "packets_received": received,
            "raw_output": "Cloud Native TCP Socket ping fallback executed successfully.",
            "error": None,
        }

    return {
        "success": False,
        "average_latency": None,
        "minimum_latency": None,
        "maximum_latency": None,
        "packet_loss": 100.0,
        "packets_sent": count,
        "packets_received": 0,
        "raw_output": "",
        "error": "Host unreachable / ICMP & TCP Probes failed.",
    }