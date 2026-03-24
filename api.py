"""
Holehe OSINT - REST API
Full REST API for checking email account registrations across 120+ platforms
including Indonesian platforms (Shopee, Tokopedia, Bukalapak, etc.)

Deploy on DirectAdmin via Passenger WSGI or run locally with:
    python api.py

Environment Variables:
    API_KEY       - (optional) Require this key via X-API-Key header or ?api_key= param
    HOST          - Bind host (default: 0.0.0.0)
    PORT          - Bind port (default: 8000)
    TIMEOUT       - Request timeout in seconds (default: 15)
    MAX_WORKERS   - Max concurrent workers (default: all modules)
"""

import os
import time
import asyncio
import importlib
import pkgutil
import re
from datetime import datetime

import httpx
import trio
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# ─── holehe internals ────────────────────────────────────────────────────────
from holehe.core import import_submodules, get_functions, is_email

# ─── Config ──────────────────────────────────────────────────────────────────
API_KEY   = os.environ.get("API_KEY", "")          # empty = no auth required
TIMEOUT   = int(os.environ.get("TIMEOUT", 15))
VERSION   = "1.0.0"

app = Flask(__name__)
CORS(app)  # Allow all origins (restrict in .htaccess if needed)

# ─── Domain map (extended with ID platforms) ─────────────────────────────────
DOMAIN_MAP = {
    'aboutme': 'about.me', 'adobe': 'adobe.com', 'amazon': 'amazon.com',
    'anydo': 'any.do', 'archive': 'archive.org', 'armurerieauxerre': 'armurerie-auxerre.com',
    'atlassian': 'atlassian.com', 'babeshows': 'babeshows.co.uk',
    'badeggsonline': 'badeggsonline.com', 'biosmods': 'bios-mods.com',
    'biotechnologyforums': 'biotechnologyforums.com', 'bitmoji': 'bitmoji.com',
    'blablacar': 'blablacar.com', 'blackworldforum': 'blackworldforum.com',
    'blip': 'blip.fm', 'blitzortung': 'forum.blitzortung.org',
    'bluegrassrivals': 'bluegrassrivals.com', 'bodybuilding': 'bodybuilding.com',
    'buymeacoffee': 'buymeacoffee.com', 'cambridgemt': 'discussion.cambridge-mt.com',
    'caringbridge': 'caringbridge.org', 'chinaphonearena': 'chinaphonearena.com',
    'clashfarmer': 'clashfarmer.com', 'codecademy': 'codecademy.com',
    'codeigniter': 'forum.codeigniter.com', 'codepen': 'codepen.io',
    'coroflot': 'coroflot.com', 'cpaelites': 'cpaelites.com', 'cpahero': 'cpahero.com',
    'cracked_to': 'cracked.to', 'crevado': 'crevado.com', 'deliveroo': 'deliveroo.com',
    'demonforums': 'demonforums.net', 'devrant': 'devrant.com', 'diigo': 'diigo.com',
    'discord': 'discord.com', 'docker': 'docker.com', 'dominosfr': 'dominos.fr',
    'ebay': 'ebay.com', 'ello': 'ello.co', 'envato': 'envato.com',
    'eventbrite': 'eventbrite.com', 'evernote': 'evernote.com', 'fanpop': 'fanpop.com',
    'firefox': 'firefox.com', 'flickr': 'flickr.com', 'freelancer': 'freelancer.com',
    'freiberg': 'drachenhort.user.stunet.tu-freiberg.de', 'garmin': 'garmin.com',
    'github': 'github.com', 'google': 'google.com', 'gravatar': 'gravatar.com',
    'hubspot': 'hubspot.com', 'imgur': 'imgur.com', 'insightly': 'insightly.com',
    'instagram': 'instagram.com', 'issuu': 'issuu.com', 'koditv': 'forum.kodi.tv',
    'komoot': 'komoot.com', 'laposte': 'laposte.fr', 'lastfm': 'last.fm',
    'lastpass': 'lastpass.com', 'mail_ru': 'mail.ru', 'mybb': 'community.mybb.com',
    'myspace': 'myspace.com', 'nattyornot': 'nattyornotforum.nattyornot.com',
    'naturabuy': 'naturabuy.fr', 'ndemiccreations': 'forum.ndemiccreations.com',
    'nextpvr': 'forums.nextpvr.com', 'nike': 'nike.com', 'nimble': 'nimble.com',
    'nocrm': 'nocrm.io', 'nutshell': 'nutshell.com', 'odnoklassniki': 'ok.ru',
    'office365': 'office365.com', 'onlinesequencer': 'onlinesequencer.net',
    'parler': 'parler.com', 'patreon': 'patreon.com', 'pinterest': 'pinterest.com',
    'pipedrive': 'pipedrive.com', 'plurk': 'plurk.com', 'pornhub': 'pornhub.com',
    'protonmail': 'protonmail.ch', 'quora': 'quora.com', 'rambler': 'rambler.ru',
    'redtube': 'redtube.com', 'replit': 'replit.com', 'rocketreach': 'rocketreach.co',
    'samsung': 'samsung.com', 'seoclerks': 'seoclerks.com', 'sevencups': '7cups.com',
    'smule': 'smule.com', 'snapchat': 'snapchat.com', 'soundcloud': 'soundcloud.com',
    'sporcle': 'sporcle.com', 'spotify': 'spotify.com', 'strava': 'strava.com',
    'taringa': 'taringa.net', 'teamleader': 'teamleader.eu',
    'teamtreehouse': 'teamtreehouse.com', 'tellonym': 'tellonym.me',
    'thecardboard': 'thecardboard.org', 'therianguide': 'forums.therian-guide.com',
    'thevapingforum': 'thevapingforum.com', 'tumblr': 'tumblr.com',
    'tunefind': 'tunefind.com', 'twitter': 'twitter.com', 'venmo': 'venmo.com',
    'vivino': 'vivino.com', 'voxmedia': 'voxmedia.com', 'vrbo': 'vrbo.com',
    'vsco': 'vsco.co', 'wattpad': 'wattpad.com', 'wordpress': 'wordpress.com',
    'xing': 'xing.com', 'xnxx': 'xnxx.com', 'xvideos': 'xvideos.com',
    'yahoo': 'yahoo.com', 'zoho': 'zoho.com', 'axonaut': 'axonaut.com',
    'amocrm': 'amocrm.com',
    # Indonesian platforms
    'shopee': 'shopee.co.id', 'tokopedia': 'tokopedia.com',
    'bukalapak': 'bukalapak.com', 'blibli': 'blibli.com',
    'lazada_id': 'lazada.co.id', 'traveloka': 'traveloka.com',
    'tiketcom': 'tiket.com', 'gojek': 'gojek.com',
    'kaskus': 'kaskus.co.id', 'dana': 'dana.id',
}


# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_api_key():
    return (
        request.headers.get("X-API-Key")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
        or request.args.get("api_key", "")
    )


def auth_required(f):
    """Decorator: enforce API key if API_KEY env var is set."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if API_KEY and get_api_key() != API_KEY:
            return jsonify({
                "success": False,
                "error": "Unauthorized. Provide a valid X-API-Key header or ?api_key= parameter."
            }), 401
        return f(*args, **kwargs)
    return decorated


def load_all_modules():
    """Import all holehe modules and return list of async functions."""
    modules = import_submodules("holehe.modules")
    return get_functions(modules)


def load_modules_info():
    """Return metadata for each module."""
    raw = import_submodules("holehe.modules")
    result = []
    for key, mod in raw.items():
        parts = key.split(".")
        if len(parts) <= 3:
            continue
        category = parts[2]   # e.g. "shopping"
        site_name = parts[-1]  # e.g. "shopee"
        fn = mod.__dict__.get(site_name)
        if fn is None:
            continue
        result.append({
            "name": site_name,
            "category": category,
            "domain": DOMAIN_MAP.get(site_name, ""),
        })
    return sorted(result, key=lambda x: x["name"])


async def _run_check(email: str, modules, timeout: int = TIMEOUT):
    """Run holehe async checks and return raw results list."""
    out = []
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        async with trio.open_nursery() as nursery:
            for mod in modules:
                nursery.start_soon(_safe_run, mod, email, client, out)
    return sorted(out, key=lambda x: x.get("name", ""))


async def _safe_run(module_fn, email, client, out):
    """Wrap a module call so errors become structured entries."""
    try:
        await module_fn(email, client, out)
    except Exception as exc:
        name = getattr(module_fn, "__name__", "unknown")
        out.append({
            "name": name,
            "domain": DOMAIN_MAP.get(name, ""),
            "method": "unknown",
            "rateLimit": False,
            "error": True,
            "exists": False,
            "emailrecovery": None,
            "phoneNumber": None,
            "others": {"errorMessage": str(exc)},
        })


def run_trio(coro):
    """Run a trio async function synchronously (Flask-compatible)."""
    return trio.from_thread.run_sync(lambda: trio.run(coro)) if False else trio.run(coro)


def check_email_sync(email: str, modules):
    """Synchronous wrapper around trio check."""
    return trio.run(_run_check, email, modules)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """API Info."""
    all_modules = load_modules_info()
    return jsonify({
        "success": True,
        "name": "Holehe OSINT REST API",
        "version": VERSION,
        "description": (
            "Check if an email address is registered on 120+ websites "
            "including Indonesian platforms (Shopee, Tokopedia, Bukalapak, etc.)"
        ),
        "total_modules": len(all_modules),
        "endpoints": {
            "GET  /": "API info",
            "GET  /health": "Health check",
            "GET  /openapi.json": "OpenAPI 3.0 specification (JSON)",
            "GET  /docs": "Swagger UI interactive documentation",
            "GET  /redoc": "ReDoc documentation",
            "GET  /modules": "List all modules",
            "GET  /modules/{category}": "List modules by category",
            "GET  /check/{email}": "Check email (all modules)",
            "POST /check": "Check email (all modules, body: {email})",
            "POST /check/modules": "Check email against specific modules (body: {email, modules:[]})",
        },
        "auth": "X-API-Key header or ?api_key= query param" if API_KEY else "none",
    })


# ─── OpenAPI / Swagger / ReDoc ───────────────────────────────────────────────

def _build_openapi_spec():
    """Build a complete OpenAPI 3.0 spec dict from the current API."""
    auth_scheme = [
        {"ApiKeyAuth": []}
    ] if API_KEY else []

    result_entry = {
        "type": "object",
        "properties": {
            "name":          {"type": "string", "example": "instagram"},
            "domain":        {"type": "string", "example": "instagram.com"},
            "method":        {"type": "string", "example": "register"},
            "exists":        {"type": "boolean"},
            "rateLimit":     {"type": "boolean"},
            "emailrecovery": {"type": "string", "nullable": True},
            "phoneNumber":   {"type": "string", "nullable": True},
            "others":        {"type": "object",  "nullable": True},
        }
    }

    check_response = {
        "type": "object",
        "properties": {
            "success":         {"type": "boolean"},
            "email":           {"type": "string"},
            "timestamp":       {"type": "string", "format": "date-time"},
            "elapsed_seconds": {"type": "number"},
            "summary": {
                "type": "object",
                "properties": {
                    "total_checked": {"type": "integer"},
                    "found":         {"type": "integer"},
                    "not_found":     {"type": "integer"},
                    "rate_limited":  {"type": "integer"},
                    "errors":        {"type": "integer"},
                }
            },
            "results": {
                "type": "object",
                "properties": {
                    "found":        {"type": "array", "items": result_entry},
                    "not_found":    {"type": "array", "items": result_entry},
                    "rate_limited": {"type": "array", "items": result_entry},
                    "errors":       {"type": "array", "items": result_entry},
                }
            }
        }
    }

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Holehe OSINT REST API",
            "version": VERSION,
            "description": (
                "Check if an email is registered on **133+ websites** including "
                "Indonesian platforms (Shopee, Tokopedia, Bukalapak, Blibli, Lazada ID, "
                "Traveloka, Tiket.com, Gojek, Kaskus, DANA).\n\n"
                "Results are grouped into: `found`, `not_found`, `rate_limited`, `errors`."
            ),
            "contact": {"email": "megadose@protonmail.com"},
            "license": {"name": "GPL-3.0", "url": "https://www.gnu.org/licenses/gpl-3.0.html"},
        },
        "servers": [{"url": "/", "description": "Current server"}],
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Optional API key (required only if API_KEY env var is set)",
                }
            },
            "schemas": {
                "ResultEntry": result_entry,
                "CheckResponse": check_response,
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": False},
                        "error":   {"type": "string"},
                    }
                },
            }
        },
        "paths": {
            "/": {
                "get": {
                    "summary": "API Info",
                    "description": "Returns API metadata, version, and list of all endpoints.",
                    "operationId": "getInfo",
                    "tags": ["Info"],
                    "responses": {"200": {"description": "API info"}},
                }
            },
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "operationId": "healthCheck",
                    "tags": ["Info"],
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {"application/json": {"schema": {
                                "type": "object",
                                "properties": {
                                    "success":   {"type": "boolean"},
                                    "status":    {"type": "string", "example": "healthy"},
                                    "timestamp": {"type": "string"},
                                    "version":   {"type": "string"},
                                }
                            }}}
                        }
                    }
                }
            },
            "/modules": {
                "get": {
                    "summary": "List All Modules",
                    "description": "Returns all 133+ holehe modules grouped by category.",
                    "operationId": "listModules",
                    "tags": ["Modules"],
                    "security": auth_scheme,
                    "responses": {"200": {"description": "Module list"}},
                }
            },
            "/modules/{category}": {
                "get": {
                    "summary": "List Modules by Category",
                    "operationId": "listModulesByCategory",
                    "tags": ["Modules"],
                    "security": auth_scheme,
                    "parameters": [{
                        "name": "category",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "example": "shopping"},
                        "description": "Category name (e.g. shopping, social_media, payment, transport, forum)",
                    }],
                    "responses": {
                        "200": {"description": "Filtered module list"},
                        "404": {"description": "Category not found",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                    },
                }
            },
            "/check/{email}": {
                "get": {
                    "summary": "Check Email (GET)",
                    "description": "Check an email against all 133+ modules. Results are split into found / not_found / rate_limited / errors.",
                    "operationId": "checkEmailGet",
                    "tags": ["Check"],
                    "security": auth_scheme,
                    "parameters": [{
                        "name": "email",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "example": "test@gmail.com"},
                    }],
                    "responses": {
                        "200": {"description": "Scan results",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CheckResponse"}}}},
                        "422": {"description": "Invalid email",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                    },
                }
            },
            "/check": {
                "post": {
                    "summary": "Check Email (POST)",
                    "description": "Check an email against all 133+ modules via POST JSON body.",
                    "operationId": "checkEmailPost",
                    "tags": ["Check"],
                    "security": auth_scheme,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {
                            "type": "object",
                            "required": ["email"],
                            "properties": {"email": {"type": "string", "example": "test@gmail.com"}},
                        }}}
                    },
                    "responses": {
                        "200": {"description": "Scan results",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CheckResponse"}}}},
                        "400": {"description": "Missing email field"},
                        "422": {"description": "Invalid email format"},
                    },
                }
            },
            "/check/modules": {
                "post": {
                    "summary": "Check Email Against Specific Modules",
                    "description": "Check an email against a user-specified list of modules only.",
                    "operationId": "checkEmailModules",
                    "tags": ["Check"],
                    "security": auth_scheme,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {
                            "type": "object",
                            "required": ["email", "modules"],
                            "properties": {
                                "email":   {"type": "string", "example": "test@gmail.com"},
                                "modules": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "example": ["shopee", "tokopedia", "instagram", "discord"],
                                },
                            },
                        }}}
                    },
                    "responses": {
                        "200": {"description": "Scan results",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CheckResponse"}}}},
                        "400": {"description": "Missing fields"},
                        "404": {"description": "No modules found"},
                        "422": {"description": "Invalid email format"},
                    },
                }
            },
        },
        "tags": [
            {"name": "Info",    "description": "API information and health"},
            {"name": "Modules", "description": "Browse available check modules"},
            {"name": "Check",   "description": "Run email OSINT lookups"},
        ],
    }
    return spec


@app.route("/openapi.json", methods=["GET"])
def openapi_spec():
    """OpenAPI 3.0 JSON specification."""
    import json
    return Response(
        json.dumps(_build_openapi_spec(), indent=2),
        mimetype="application/json",
    )


@app.route("/docs", methods=["GET"])
def swagger_ui():
    """Swagger UI interactive documentation."""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Holehe OSINT API — Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  <style>
    body { margin: 0; }
    #swagger-ui .topbar { background: #1a1a2e; }
    #swagger-ui .topbar-wrapper .link { display: none; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "/openapi.json",
      dom_id: "#swagger-ui",
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      tryItOutEnabled: true,
      requestInterceptor: (req) => {
        // Auto-inject API key from localStorage if available
        const key = localStorage.getItem('holehe_api_key');
        if (key) req.headers['X-API-Key'] = key;
        return req;
      },
    });
  </script>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@app.route("/redoc", methods=["GET"])
def redoc_ui():
    """ReDoc documentation UI."""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Holehe OSINT API — ReDoc</title>
  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; }
  </style>
</head>
<body>
  <redoc spec-url="/openapi.json"
         expand-responses="200"
         hide-download-button
         theme='{
           "colors": {"primary": {"main": "#6c63ff"}},
           "typography": {"fontFamily": "Roboto, sans-serif"},
           "sidebar": {"backgroundColor": "#1a1a2e", "textColor": "#ffffff"}
         }'>
  </redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": VERSION,
    })


@app.route("/modules", methods=["GET"])
@auth_required
def list_modules():
    """List all available modules."""
    all_modules = load_modules_info()
    categories = {}
    for m in all_modules:
        cat = m["category"]
        categories.setdefault(cat, []).append(m)

    return jsonify({
        "success": True,
        "total": len(all_modules),
        "categories": categories,
        "modules": all_modules,
    })


@app.route("/modules/<category>", methods=["GET"])
@auth_required
def list_modules_by_category(category):
    """List modules filtered by category."""
    all_modules = load_modules_info()
    filtered = [m for m in all_modules if m["category"].lower() == category.lower()]
    if not filtered:
        return jsonify({
            "success": False,
            "error": f"Category '{category}' not found or has no modules.",
            "available_categories": sorted(set(m["category"] for m in all_modules)),
        }), 404
    return jsonify({
        "success": True,
        "category": category,
        "total": len(filtered),
        "modules": filtered,
    })


@app.route("/check/<path:email>", methods=["GET"])
@auth_required
def check_get(email):
    """Check email via GET /check/<email>"""
    only_found = request.args.get("only_found", "true").lower() in ("true", "1", "yes")
    return _do_check(email, only_found=only_found)


@app.route("/check", methods=["POST"])
@auth_required
def check_post():
    """Check email via POST /check with JSON body {email: '...'}"""
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    only_found = body.get("only_found", True)
    if not isinstance(only_found, bool):
        only_found = str(only_found).lower() in ("true", "1", "yes")

    if not email:
        return jsonify({"success": False, "error": "Missing 'email' field in request body."}), 400
    return _do_check(email, only_found=only_found)


@app.route("/check/modules", methods=["POST"])
@auth_required
def check_specific_modules():
    """
    Check email against specific modules.
    Body: {"email": "...", "modules": ["instagram", "shopee"], "only_found": true}
    """
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    requested = body.get("modules", [])
    only_found = body.get("only_found", True)
    if not isinstance(only_found, bool):
        only_found = str(only_found).lower() in ("true", "1", "yes")

    if not email:
        return jsonify({"success": False, "error": "Missing 'email' field."}), 400
    if not isinstance(requested, list) or not requested:
        return jsonify({"success": False, "error": "Missing or empty 'modules' list."}), 400

    if not is_email(email):
        return jsonify({"success": False, "error": f"'{email}' is not a valid email address."}), 422

    all_fns = load_all_modules()
    fn_map = {fn.__name__: fn for fn in all_fns}

    selected = []
    not_found = []
    for name in requested:
        if name in fn_map:
            selected.append(fn_map[name])
        else:
            not_found.append(name)

    if not selected:
        return jsonify({
            "success": False,
            "error": "None of the requested modules were found.",
            "not_found": not_found,
        }), 404

    start = time.time()
    raw = check_email_sync(email, selected)
    elapsed = round(time.time() - start, 3)

    return jsonify(_build_response(email, raw, elapsed, not_found=not_found, only_found=only_found))


def _do_check(email: str, only_found: bool = False):
    """Shared logic for full-email scan."""
    email = email.strip()
    if not is_email(email):
        return jsonify({
            "success": False,
            "error": f"'{email}' is not a valid email address.",
        }), 422

    try:
        modules = load_all_modules()
        start = time.time()
        raw = check_email_sync(email, modules)
        elapsed = round(time.time() - start, 3)
        return jsonify(_build_response(email, raw, elapsed, only_found=only_found))
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


def _build_response(email: str, raw: list, elapsed: float, not_found: list = None, only_found: bool = False):
    """Build a clean structured API response from raw holehe output."""
    found = []
    not_found_sites = []
    rate_limited = []
    errored = []

    for r in raw:
        name = r.get("name", "")
        entry = {
            "name": name,
            "domain": r.get("domain", DOMAIN_MAP.get(name, "")),
            "method": r.get("method", ""),
            "exists": r.get("exists", False),
            "rateLimit": r.get("rateLimit", False),
            "emailrecovery": r.get("emailrecovery"),
            "phoneNumber": r.get("phoneNumber"),
            "others": r.get("others"),
        }
        if r.get("error"):
            errored.append(entry)
        elif r.get("rateLimit"):
            rate_limited.append(entry)
        elif r.get("exists"):
            found.append(entry)
        else:
            not_found_sites.append(entry)

    results = {
        "found": found,
        "not_found": not_found_sites,
        "rate_limited": rate_limited,
        "errors": errored,
    }

    if only_found:
        results = {"found": found}

    resp = {
        "success": True,
        "email": email,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "elapsed_seconds": elapsed,
        "summary": {
            "total_checked": len(raw),
            "found": len(found),
            "not_found": len(not_found_sites),
            "rate_limited": len(rate_limited),
            "errors": len(errored),
        },
        "results": results,
    }
    if not_found and not only_found:  # modules that weren't resolved
        resp["unresolved_modules"] = not_found
    return resp


# ─── 404 / 405 handlers ──────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed."}), 405


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    print(f"[*] Holehe OSINT API v{VERSION}")
    print(f"[*] Listening on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
