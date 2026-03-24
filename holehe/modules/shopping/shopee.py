from holehe.core import *
from holehe.localuseragent import *


async def shopee(email, client, out):
    name = "shopee"
    domain = "shopee.co.id"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": "https://shopee.co.id/",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        data = {
            "email": email,
        }
        req = await client.post(
            "https://shopee.co.id/api/v2/user/check_email_existed/",
            json=data,
            headers=headers,
        )
        resp = req.json()

        # Shopee returns error code 0 if email is available, non-zero if taken
        if resp.get("error") != 0:
            out.append({
                "name": name, "domain": domain, "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True,
                "emailrecovery": None,
                "phoneNumber": None,
                "others": None,
            })
        else:
            out.append({
                "name": name, "domain": domain, "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False,
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
