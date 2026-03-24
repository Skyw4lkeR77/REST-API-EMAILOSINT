from holehe.core import *
from holehe.localuseragent import *


async def rocketreach(email, client, out):
    name = "rocketreach"
    domain = "rocketreach.co"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://rocketreach.co/signup",
    }

    try:
        r = await client.get(
            f"https://rocketreach.co/v1/validateEmail?email_address={email}",
            headers=headers,
        )
        if r.status_code != 200:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return
        resp = r.json()
        # API changed — key may be "found", "isFound", or nested
        found = resp.get("found", resp.get("isFound", resp.get("exists", None)))
        if found is True:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": True,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
        elif found is False:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False,
                    "emailrecovery": None, "phoneNumber": None, "others": None})
