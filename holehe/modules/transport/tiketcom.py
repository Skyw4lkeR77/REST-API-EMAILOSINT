from holehe.core import *
from holehe.localuseragent import *


async def tiketcom(email, client, out):
    name = "tiketcom"
    domain = "tiket.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.tiket.com",
        "Referer": "https://www.tiket.com/login",
    }

    try:
        payload = {"email": email}
        req = await client.post(
            "https://api.tiket.com/v2/user/check-email",
            json=payload,
            headers=headers,
        )
        resp = req.json()
        # tiket.com: {"output": {"status": "exist"}} or "not_exist"
        status = resp.get("output", {}).get("status", "not_exist")
        out.append({
            "name": name, "domain": domain, "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": status == "exist",
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
