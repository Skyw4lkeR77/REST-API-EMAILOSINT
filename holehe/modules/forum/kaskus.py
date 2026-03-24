from holehe.core import *
from holehe.localuseragent import *


async def kaskus(email, client, out):
    name = "kaskus"
    domain = "kaskus.co.id"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.kaskus.co.id",
        "Referer": "https://www.kaskus.co.id/register",
    }

    try:
        data = {"email": email}
        req = await client.post(
            "https://www.kaskus.co.id/ajax/user/check_email",
            data=data,
            headers=headers,
        )
        resp = req.json()
        # Kaskus: {"status": 1} means email taken, {"status": 0} means available
        status = resp.get("status", 0)
        out.append({
            "name": name, "domain": domain, "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": status == 1 or status is True,
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
