# Gunicorn Configuration File
# NoBan - noban.chbk.dev

import multiprocessing

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/noban/gunicorn-access.log"
errorlog = "/var/log/noban/gunicorn-error.log"
loglevel = "info"

# Process Naming
proc_name = "noban"

# Server Mechanics
daemon = False
pidfile = "/tmp/noban-gunicorn.pid"
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
