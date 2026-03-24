from holehe.core import *
from holehe.localuseragent import *


async def dana(email, client, out):
    name = "dana"
    domain = "dana.id"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.dana.id",
        "Referer": "https://www.dana.id/register",
    }

    try:
        payload = {
            "request": {
                "email": email,
            }
        }
        req = await client.post(
            "https://m.dana.id/d/dana/v1.0/user-register/check-email.htm",
            json=payload,
            headers=headers,
        )
        resp = req.json()
        # DANA: {"response": {"body": {"isRegistered": true}}}
        is_registered = resp.get("response", {}).get("body", {}).get("isRegistered", False)
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
