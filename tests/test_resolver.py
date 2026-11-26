import socket
import threading

import config
import resolver


def fake_upstream(reply_fn):
    """Un 'upstream' fals pe localhost, care răspunde o singură dată."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]

    def run():
        sock.settimeout(2)
        try:
            data, addr = sock.recvfrom(4096)
            sock.sendto(reply_fn(data), addr)
        except OSError:
            pass
        finally:
            sock.close()

    threading.Thread(target=run, daemon=True).start()
    return port


def test_forward_returns_reply_with_same_id(monkeypatch):
    port = fake_upstream(lambda d: d + b"x")
    monkeypatch.setattr(config, "UPSTREAM_HOST", "127.0.0.1")
    monkeypatch.setattr(config, "UPSTREAM_PORT", port)
    assert resolver.forward(b"\x12\x34abc", timeout=1) == b"\x12\x34abcx"


def test_forward_ignores_wrong_id(monkeypatch):
    port = fake_upstream(lambda d: b"\xff\xff" + d[2:])
    monkeypatch.setattr(config, "UPSTREAM_HOST", "127.0.0.1")
    monkeypatch.setattr(config, "UPSTREAM_PORT", port)
    assert resolver.forward(b"\x12\x34abc", timeout=1) is None
