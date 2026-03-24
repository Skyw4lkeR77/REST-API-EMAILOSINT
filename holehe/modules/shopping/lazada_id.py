from holehe.core import *
from holehe.localuseragent import *


async def lazada_id(email, client, out):
    name = "lazada_id"
    domain = "lazada.co.id"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://member.lazada.co.id",
        "Referer": "https://member.lazada.co.id/user/register",
    }

    try:
        data = {"email": email, "countryCode": "ID"}
        req = await client.post(
            "https://member.lazada.co.id/user/api/checkEmailExist",
            data=data,
            headers=headers,
        )
        resp = req.json()
        # Lazada: {"success": true, "result": {"isExist": true}}
        is_exist = resp.get("result", {}).get("isExist", False)
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
