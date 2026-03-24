from holehe.core import *
from holehe.localuseragent import *


async def buymeacoffee(email, client, out):
    name = "buymeacoffee"
    domain = "buymeacoffee.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.buymeacoffee.com",
    }

    try:
        r = await client.get("https://www.buymeacoffee.com/", headers=headers)
        if r.status_code != 200:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return

        soup = BeautifulSoup(r.content, features="html.parser")
        csrf_tag = soup.find(attrs={"name": "bmc_csrf_token"})
        if csrf_tag is None:
            # CSRF token not found — page changed, treat as rate limit
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return

        csrf_token = csrf_tag.get("value", "")
        data = {
            "email": email,
            "password": "".join(random.choice(string.ascii_lowercase) for _ in range(20)),
            "bmc_csrf_token": csrf_token,
        }
        r2 = await client.post(
            "https://www.buymeacoffee.com/auth/validate_email_and_password",
            headers=headers,
            cookies={"bmccsrftoken": csrf_token},
            data=data,
        )
        if r2.status_code == 200:
            resp = r2.json()
            status = resp.get("status", "")
            if status == "FAIL" and "email" in str(resp).lower():
                out.append({"name": name, "domain": domain, "method": method,
                            "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": False, "exists": True,
                            "emailrecovery": None, "phoneNumber": None, "others": None})
            elif status == "SUCCESS":
                out.append({"name": name, "domain": domain, "method": method,
                            "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": False, "exists": False,
                            "emailrecovery": None, "phoneNumber": None, "others": None})
            else:
                out.append({"name": name, "domain": domain, "method": method,
                            "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": True, "exists": False,
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
