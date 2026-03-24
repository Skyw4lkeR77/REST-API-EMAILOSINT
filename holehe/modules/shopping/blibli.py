from holehe.core import *
from holehe.localuseragent import *


async def blibli(email, client, out):
    name = "blibli"
    domain = "blibli.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.blibli.com",
        "Referer": "https://www.blibli.com/register",
    }

    try:
        req = await client.get(
            f"https://www.blibli.com/backend/api/v2.0/users/check-email?email={email}",
            headers=headers,
        )
        resp = req.json()
        # Blibli: {"code": 200, "data": {"isExist": true}}
        is_exist = resp.get("data", {}).get("isExist", False)
        out.append({
            "name": name, "domain": domain, "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": bool(is_exist),
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
