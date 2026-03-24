"""
passenger_wsgi.py - DirectAdmin / cPanel Passenger WSGI Entry Point

DirectAdmin uses Phusion Passenger to serve Python apps.
This file is the WSGI entry point that Passenger looks for automatically.

Setup steps on DirectAdmin:
  1. Upload project files to your domain's public_html or a subdirectory
  2. In DirectAdmin > Domains > Python App, set:
       - Python version: 3.x
       - Application startup file: passenger_wsgi.py
       - Application Entry Point: application
  3. Install dependencies:
       pip install -r requirements.txt --user
  4. Set environment variables via .env or DirectAdmin's ENV settings
  5. Restart the app via DirectAdmin or: touch tmp/restart.txt
"""

import sys
import os

# ── Add project root to path ──────────────────────────────────────────────────
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

# ── Load .env if present ──────────────────────────────────────────────────────
env_file = os.path.join(here, ".env")
if os.path.isfile(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

# ── Import the Flask app ──────────────────────────────────────────────────────
from api import app as application  # noqa: E402

# Passenger expects the WSGI callable to be named `application`
