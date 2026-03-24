from holehe.core import *
from holehe.localuseragent import *


async def evernote(email, client, out):
    name = "evernote"
    domain = "evernote.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.evernote.com",
        "Referer": "https://www.evernote.com/Login.action",
    }

    try:
        page = await client.get("https://www.evernote.com/Login.action", headers=headers)
        page_text = page.text

        def extract(marker):
            try:
                return page_text.split(marker)[1].split('"')[0]
            except IndexError:
                return ""

        hpts  = extract('document.getElementById("hpts").value = "')
        hptsh = extract('document.getElementById("hptsh").value = "')
        src   = extract('<input type="hidden" name="_sourcePage" value="')
        fp    = extract('<input type="hidden" name="__fp" value="')

        if not hpts or not src:
            # Page structure changed — fall back to rate limit
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
            return

        data = {
            "username": email, "evaluateUsername": "",
            "hpts": hpts, "hptsh": hptsh,
            "analyticsLoginOrigin": "login_action", "clipperFlow": "false",
            "showSwitchService": "true", "usernameImmutable": "false",
            "_sourcePage": src, "__fp": fp,
        }
        response = await client.post(
            "https://www.evernote.com/Login.action", data=data, headers=headers
        )
        if "usePasswordAuth" in response.text:
            out.append({"name": name, "domain": domain, "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": True,
                        "emailrecovery": None, "phoneNumber": None, "others": None})
        elif "displayMessage" in response.text:
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
