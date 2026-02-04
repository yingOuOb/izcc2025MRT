"""Gunicorn configuration file for Flask-SocketIO application."""
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = 1
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5

# Threading
threads = 1

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "izcc2025MRT"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None
