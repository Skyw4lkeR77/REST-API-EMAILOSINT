from holehe.core import *
from holehe.localuseragent import *


async def samsung(email, client, out):
    name = "samsung"
    domain = "samsung.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://account.samsung.com",
        "Referer": "https://account.samsung.com/accounts/v1/Samsung_com/signUp",
    }

    try:
        # Get CSRF token from Samsung sign-up page
        page_req = await client.get(
            "https://account.samsung.com/accounts/v1/Samsung_com/signUp",
            headers={"User-Agent": random.choice(ua["browsers"]["chrome"])},
        )
        page_text = page_req.text

        # Extract CSRF token — try multiple patterns
        csrf = None
        for pattern in [r"'token'\s*:\s*'([^']+)'", r'"token"\s*:\s*"([^"]+)"',
                        r"csrfToken['\"]?\s*:\s*['\"]([^'\"]+)"]:
            m = re.search(pattern, page_text)
            if m:
                csrf = m.group(1)
                break

        if not csrf:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return

        headers["X-CSRF-TOKEN"] = csrf
        data = json.dumps({"emailID": email})
        req = await client.post(
            "https://account.samsung.com/accounts/v1/Samsung_com/signUpCheckEmailIDProc",
            headers=headers,
            content=data,
        )
        resp = req.json()
        if req.status_code == 200 and "rtnCd" in resp:
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
