import logging
import os
import threading
from collections import Counter

ACTIONS = {"BLOCKED", "CACHED", "FORWARDED", "RATE_LIMITED", "FAILED"}

_logger = logging.getLogger("dnsproxy")
_logger.setLevel(logging.INFO)
_logger.propagate = False

_lock = threading.Lock()
_stats = Counter()
_blocked_domains = Counter()
_clients = Counter()

def setup(log_dir="logs"):
    """Porneste scrierea in fisierul: logs/queries.log"""
    os.makedirs(log_dir, exist_ok=True)
    close()
    handler = logging.FileHandler(
        os.path.join(log_dir, "queries.log"),encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    _logger.addHandler(handler)

def close():
    for handler in list(_logger.handlers):
        handler.close()
        _logger.removeHandler(handler)

def log_query(ip, domain, qtype, action, ms):
    if action not in ACTIONS:
        raise ValueError(f"actiune necunoscuta: {action}")
    _logger.info("%s %s %s %s %.1fms", ip, qtype, domain, action, ms)
    with _lock:
        _stats[action] += 1
        _clients[ip] += 1
        if action == "BLOCKED":
            _blocked_domains[domain] += 1

def get_stats():
    with _lock:
        return {
            "total": sum(_stats.values()),
            "by_action": dict(_stats),
            "top_blocked": _blocked_domains.most_common(10),
            "top_clients": _clients.most_common(10),
        }

def  reset():
    with _lock:
        _stats.clear()
        _blocked_domains.clear()
        _clients.clear()