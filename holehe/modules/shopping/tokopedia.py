from holehe.core import *
from holehe.localuseragent import *


async def tokopedia(email, client, out):
    name = "tokopedia"
    domain = "tokopedia.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.tokopedia.com",
        "Referer": "https://www.tokopedia.com/login",
    }

    try:
        # Tokopedia GraphQL API for checking email
        payload = {
            "operationName": "CheckEmail",
            "variables": {"email": email},
            "query": "query CheckEmail($email: String!) { checkEmail(email: $email) { isExist } }",
        }
        req = await client.post(
            "https://accounts.tokopedia.com/api/v1/auth/check-email",
            json={"email": email},
            headers=headers,
        )
        resp = req.json()

        is_exist = resp.get("data", {}).get("isExist", False)
        # Also check the status / errors field
        if is_exist or resp.get("isExist") is True:
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
            # Try alternative endpoint
            req2 = await client.get(
                f"https://accounts.tokopedia.com/api/v1/sso-check?email={email}",
                headers=headers,
            )
            resp2 = req2.json()
            exists = resp2.get("data", {}).get("exists", False)
            out.append({
                "name": name, "domain": domain, "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": bool(exists),
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
