from holehe.core import *
from holehe.localuseragent import *


async def snapchat(email, client, out):
    name = "snapchat"
    domain = "snapchat.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Snapchat-Client-Auth-Token": "Bearer ",
    }

    try:
        # Snapchat account lookup via sign-up check API
        payload = {"email": email}
        req = await client.post(
            "https://accounts.snapchat.com/accounts/v2/check_email_exists",
            json=payload,
            headers=headers,
        )
        resp = req.json()
        exists = resp.get("email_exists", resp.get("emailExists", False))
        out.append({"name": name, "domain": domain, "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": bool(exists),
                    "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False,
                    "emailrecovery": None, "phoneNumber": None, "others": None})
