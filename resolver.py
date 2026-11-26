import socket
import time

import config


def forward(data, timeout=3):
    """Trimite cererea la upstream. Întoarce răspunsul (bytes) sau None."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(data, (config.UPSTREAM_HOST, config.UPSTREAM_PORT))
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            s.settimeout(remaining)
            try:
                reply, addr = s.recvfrom(4096)
            except TimeoutError:
                return None
            # acceptăm doar răspunsuri de la upstream, cu același ID ca cererea
            if addr[0] == config.UPSTREAM_HOST and reply[:2] == data[:2]:
                return reply
    except OSError:
        return None
    finally:
        s.close()
