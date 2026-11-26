import os

LISTEN_HOST = os.environ.get("LISTEN_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", 5300))
UPSTREAM_HOST = os.environ.get("UPSTREAM_HOST", "1.1.1.1")
UPSTREAM_PORT = 53
