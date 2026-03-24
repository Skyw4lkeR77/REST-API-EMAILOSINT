from holehe.core import *
from holehe.localuseragent import *


async def pinterest(email, client, out):
    name = "pinterest"
    domain = "pinterest.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.pinterest.com/",
    }

    try:
        req = await client.get(
            "https://www.pinterest.com/_ngjs/resource/EmailExistsResource/get/",
            params={
                "source_url": "/",
                "data": '{"options": {"email": "' + email + '"}, "context": {}}',
            },
            headers=headers,
        )
        if req.status_code != 200:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return

        resp = req.json()
        data = resp.get("resource_response", {}).get("data")
        if data is None:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return

        if "source_field" in str(data):
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
        elif data:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": True,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False,
                    "emailrecovery": None, "phoneNumber": None, "others": None})
