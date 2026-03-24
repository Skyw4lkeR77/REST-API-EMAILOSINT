from holehe.core import *
from holehe.localuseragent import *


async def soundcloud(email, client, out):
    name = "soundcloud"
    domain = "soundcloud.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
    }

    try:
        # Use SoundCloud's public identifier check API with a known client_id
        # This client_id is embedded in the public SoundCloud web app
        client_id = "iZIs9mchVcX5lhVRyQGGAYlNPVldzAoX"
        email_enc = email.replace("@", "%40")
        req = await client.get(
            f"https://api-auth.soundcloud.com/web-auth/identifier?q={email_enc}&client_id={client_id}",
            headers=headers,
        )
        if req.status_code != 200:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return
        resp = req.json()
        status = resp.get("status", "available")
        out.append({"name": name, "domain": domain, "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": (status == "in_use"),
                    "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False,
                    "emailrecovery": None, "phoneNumber": None, "others": None})
