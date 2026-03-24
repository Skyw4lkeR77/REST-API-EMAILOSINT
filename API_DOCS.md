# Holehe OSINT REST API — Documentation

> Check if an email is registered on **130+ websites** including Indonesian platforms  
> (Shopee, Tokopedia, Bukalapak, Blibli, Lazada ID, Traveloka, Tiket.com, Gojek, Kaskus, DANA)

---

## Base URL

```
http://yourdomain.com/          # local dev
https://api.yourdomain.com/     # production
```

---

## Authentication

If `API_KEY` is set in `.env`, every request must include the key via **one** of:

| Method | Example |
|--------|---------|
| Header | `X-API-Key: your-secret-key` |
| Header | `Authorization: Bearer your-secret-key` |
| Query  | `?api_key=your-secret-key` |

If `API_KEY` is empty, the API is public (no auth needed).

---

## Endpoints

### `GET /`
API info and list of all available endpoints.

**Response**
```json
{
  "success": true,
  "name": "Holehe OSINT REST API",
  "version": "1.0.0",
  "total_modules": 130,
  "endpoints": { ... }
}
```

---

### `GET /health`
Health check — use this to verify the service is running.

**Response**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-03-24T05:45:00Z",
  "version": "1.0.0"
}
```

---

### `GET /modules`
List all available modules grouped by category.

**Response**
```json
{
  "success": true,
  "total": 130,
  "categories": {
    "shopping": [
      { "name": "shopee",    "category": "shopping", "domain": "shopee.co.id" },
      { "name": "tokopedia", "category": "shopping", "domain": "tokopedia.com" },
      ...
    ],
    "social_media": [ ... ]
  },
  "modules": [ ... ]
}
```

---

### `GET /modules/{category}`
List modules for a specific category.

**Categories:** `shopping`, `social_media`, `forum`, `payment`, `transport`,  
`crm`, `crowfunding`, `jobs`, `learning`, `mails`, `medias`, `medical`,  
`music`, `osint`, `porn`, `productivity`, `products`, `programing`,  
`real_estate`, `software`, `sport`, `cms`, `company`

**Example:** `GET /modules/shopping`

**Response**
```json
{
  "success": true,
  "category": "shopping",
  "total": 12,
  "modules": [
    { "name": "shopee",    "domain": "shopee.co.id" },
    { "name": "tokopedia", "domain": "tokopedia.com" },
    { "name": "bukalapak", "domain": "bukalapak.com" },
    { "name": "blibli",    "domain": "blibli.com" },
    { "name": "lazada_id", "domain": "lazada.co.id" },
    { "name": "amazon",    "domain": "amazon.com" },
    ...
  ]
}
```

---

### `GET /check/{email}`
Check an email against **all** modules.

**Example:** `GET /check/test@gmail.com`

**Headers:** `X-API-Key: your-secret-key` *(if auth enabled)*

**Query Parameters:**
- `?only_found=true` *(optional)* — Filter the `results` object to **only** return the `found` array, hiding `not_found`, `rate_limited`, and `errors`.

**Response**
```json
{
  "success": true,
  "email": "test@gmail.com",
  "timestamp": "2026-03-24T05:45:00Z",
  "elapsed_seconds": 12.5,
  "summary": {
    "total_checked": 130,
    "found": 8,
    "not_found": 115,
    "rate_limited": 5,
    "errors": 2
  },
  "results": {
    "found": [
      {
        "name": "instagram",
        "domain": "instagram.com",
        "method": "register",
        "exists": true,
        "rateLimit": false,
        "emailrecovery": null,
        "phoneNumber": null,
        "others": null
      },
      {
        "name": "shopee",
        "domain": "shopee.co.id",
        "method": "register",
        "exists": true,
        "rateLimit": false,
        "emailrecovery": null,
        "phoneNumber": null,
        "others": null
      }
    ],
    "not_found": [ ... ],
    "rate_limited": [ ... ],
    "errors": [ ... ]
  }
}
```

---

### `POST /check`
Check an email against **all** modules via POST body.

**Request**
```json
{
  "email": "test@gmail.com",
  "only_found": true
}
```

**Response:** Same format as `GET /check/{email}`

---

### `POST /check/modules`
Check an email against **specific** modules only.

**Request**
```json
{
  "email": "test@gmail.com",
  "modules": ["instagram", "shopee", "tokopedia", "discord", "github"],
  "only_found": true
}
```

**Response**
```json
{
  "success": true,
  "email": "test@gmail.com",
  "elapsed_seconds": 3.2,
  "summary": {
    "total_checked": 5,
    "found": 3,
    "not_found": 1,
    "rate_limited": 1,
    "errors": 0
  },
  "results": {
    "found": [ ... ],
    "not_found": [ ... ],
    "rate_limited": [ ... ],
    "errors": []
  }
}
```

---

## Error Responses

| Code | Cause |
|------|-------|
| `400` | Missing required field |
| `401` | Invalid or missing API key |
| `404` | Endpoint not found |
| `405` | Wrong HTTP method |
| `422` | Invalid email format |
| `500` | Internal server error |

**Example:**
```json
{
  "success": false,
  "error": "'notanemail' is not a valid email address."
}
```

---

## Deployment — DirectAdmin

### Prerequisites
- Python 3.9+ enabled in DirectAdmin
- Passenger Python support enabled

### Steps

```bash
# 1. SSH into your server and navigate to public_html
cd ~/public_html

# 2. Clone / upload the project
git clone https://github.com/yourrepo/holehe-api.git email-osint
cd email-osint

# 3. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
pip install -e .          # installs holehe from local source

# 5. Set environment variables
cp .env.example .env
nano .env                 # set API_KEY, TIMEOUT, etc.

# 6. Update .htaccess
#    Replace /home/USERNAME/ with your actual home path
nano .htaccess

# 7. In DirectAdmin:
#    Domains > yourdomain.com > Python App
#    Startup file: passenger_wsgi.py
#    Entry point:  application
#    Click Save → Restart
```

### Resetting/Restarting
```bash
# DirectAdmin auto-restarts on file change:
touch tmp/restart.txt
```

---

## Deployment — Docker

```bash
# Build
docker build -t holehe-api .

# Run (no auth)
docker run -p 8000:8000 holehe-api

# Run (with API key)
docker run -p 8000:8000 -e API_KEY=mysecretkey holehe-api

# Run (custom timeout)
docker run -p 8000:8000 -e TIMEOUT=20 holehe-api
```

---

## Local Development

```bash
pip install -r requirements.txt
pip install -e .
cp .env.example .env
python api.py
```

The API will be available at `http://localhost:8000`

---

## Indonesian Platforms Supported

| Name | Domain | Category |
|------|--------|----------|
| Shopee | shopee.co.id | shopping |
| Tokopedia | tokopedia.com | shopping |
| Bukalapak | bukalapak.com | shopping |
| Blibli | blibli.com | shopping |
| Lazada ID | lazada.co.id | shopping |
| Traveloka | traveloka.com | transport |
| Tiket.com | tiket.com | transport |
| Gojek | gojek.com | transport |
| Kaskus | kaskus.co.id | forum |
| DANA | dana.id | payment |

---

## License

GNU General Public License v3.0 — built for educational purposes only.
