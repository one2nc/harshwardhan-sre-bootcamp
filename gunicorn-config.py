import os

workers = os.cpu_count() * 2 + 1

# print(os.cpu_count())

# bind = ['0.0.0.0:80']
bind = ['0.0.0.0:5000']
# Timeout for worker processes (in seconds)
timeout = 30

# Log level
loglevel = "info"

preload_app=True

worker_class="sync" # use Uvicorn class for async apps