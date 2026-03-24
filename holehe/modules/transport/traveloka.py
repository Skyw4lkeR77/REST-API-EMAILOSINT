from holehe.core import *
from holehe.localuseragent import *


async def traveloka(email, client, out):
    name = "traveloka"
    domain = "traveloka.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.traveloka.com",
        "Referer": "https://www.traveloka.com/en-id/login",
        "X-Domain": "id",
    }

    try:
        payload = {
            "fields": {"email": email},
            "clientInterface": "desktop",
        }
        req = await client.post(
            "https://api.traveloka.com/v1/user/op/auth/check-email",
            json=payload,
            headers=headers,
        )
        resp = req.json()
        # Traveloka: {"status": "OK", "data": {"isRegistered": true}}
        is_registered = resp.get("data", {}).get("isRegistered", False)
        out.append({
            "name": name, "domain": domain, "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": bool(is_registered),
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
