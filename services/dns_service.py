# import socket


# def resolve_dns(target):
#     """
#     Resolve a domain/IP and return basic DNS information.
#     """

#     try:
#         hostname = target.strip()

#         ip_address = socket.gethostbyname(hostname)

#         return {
#             "success": True,
#             "hostname": hostname,
#             "ip_address": ip_address,
#             "error": None,
#         }

#     except socket.gaierror as e:
#         return {
#             "success": False,
#             "hostname": target,
#             "ip_address": None,
#             "error": f"DNS resolution failed: {str(e)}",
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "hostname": target,
#             "ip_address": None,
#             "error": str(e),
#         }

import asyncio
import socket

async def resolve_dns(target: str) -> dict:
    """
    Asynchronous Enterprise DNS Resolution & Reverse PTR Lookup.
    """
    hostname = target.strip()
    loop = asyncio.get_event_loop()

    try:
        # Check if target is already an IP
        socket.inet_aton(hostname)
        ip_address = hostname
        try:
            # Perform reverse PTR lookup
            ptr_res = await loop.run_in_executor(None, socket.gethostbyaddr, hostname)
            resolved_hostname = ptr_res[0]
        except Exception:
            resolved_hostname = hostname
    except socket.error:
        # Resolve hostname to IP
        try:
            ip_address = await loop.run_in_executor(None, socket.gethostbyname, hostname)
            resolved_hostname = hostname
        except socket.gaierror as e:
            return {
                "success": False,
                "hostname": hostname,
                "ip_address": None,
                "error": f"DNS resolution failed: {str(e)}",
            }

    return {
        "success": True,
        "hostname": resolved_hostname,
        "ip_address": ip_address,
        "error": None,
    }