from holehe.core import *
from holehe.localuseragent import *


async def gojek(email, client, out):
    name = "gojek"
    domain = "gojek.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.gojek.com",
    }

    try:
        payload = {"email": email}
        req = await client.post(
            "https://api.gojekapi.com/goshop/v1/user/check-email",
            json=payload,
            headers=headers,
        )
        resp = req.json()
        # Gojek: {"success": true, "data": {"isExist": true}}
        is_exist = resp.get("data", {}).get("isExist", False)
        if not isinstance(is_exist, bool):
            is_exist = str(is_exist).lower() in ("true", "1")
        out.append({
            "name": name, "domain": domain, "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": is_exist,
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
