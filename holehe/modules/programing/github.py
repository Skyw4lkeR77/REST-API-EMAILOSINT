from holehe.core import *
from holehe.localuseragent import *


async def github(email, client, out):
    name = "github"
    domain = "github.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
    }

    try:
        # GitHub API endpoint for email check during signup
        req = await client.post(
            "https://github.com/signup_check/email",
            headers=headers,
            data={"value": email, "authenticity_token": ""},
        )
        if req.status_code == 422:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": True,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
        elif req.status_code == 200:
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
