"""
Gunicorn production server configuration for ResumeIQ.

Usage:
    gunicorn -c gunicorn_config.py app:app
"""

import multiprocessing
import os

# ── Workers ──
workers = 2 * multiprocessing.cpu_count() + 1
worker_class = "sync"
threads = 2

# ── Networking ──
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
timeout = 60
keepalive = 5

# ── Logging ──
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# ── Process ──
preload_app = True
max_requests = 1000
max_requests_jitter = 50
