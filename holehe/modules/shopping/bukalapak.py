from holehe.core import *
from holehe.localuseragent import *


async def bukalapak(email, client, out):
    name = "bukalapak"
    domain = "bukalapak.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.bukalapak.com",
        "Referer": "https://www.bukalapak.com/register",
    }

    try:
        req = await client.get(
            f"https://accounts.bukalapak.com/check-email?email={email}",
            headers=headers,
        )
        resp = req.json()

        # Bukalapak returns {"available": true} if not registered
        available = resp.get("available", True)
        if not available:
            out.append({
                "name": name, "domain": domain, "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True,
                "emailrecovery": None,
                "phoneNumber": None,
                "others": None,
            })
        else:
            out.append({
                "name": name, "domain": domain, "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False,
                "emailrecovery": None,
                "phoneNumber": None,
                "others": None,
            })
    except Exception:
        out.append({
            "name": name, "domain": domain, "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False,
            "emailrecovery": None,
            "phoneNumber": None,
            "others": None,
        })
