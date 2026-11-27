import socket
import time

from dnslib import QTYPE, RCODE, DNSRecord

import blocklist
import config
import resolver


def make_reply(req, rcode):
    reply = req.reply()
    reply.header.rcode = rcode
    return reply.pack()


def handle_query(data):
    """Procesează o cerere. Întoarce (răspuns, action, domain, qtype)."""
    req = DNSRecord.parse(data)
    domain = str(req.q.qname).rstrip(".").lower()
    qtype = QTYPE.get(req.q.qtype, str(req.q.qtype))
    if blocklist.is_blocked(domain):
        return make_reply(req, RCODE.NXDOMAIN), "BLOCKED", domain, qtype
    reply_data = resolver.forward(data)
    if reply_data is None:
        return make_reply(req, RCODE.SERVFAIL), "FAILED", domain, qtype
    return reply_data, "FORWARDED", domain, qtype


def main():
    count = blocklist.load(config.BLOCKLIST_PATH)
    print(f"Blocklist: {count} domenii")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.LISTEN_HOST, config.LISTEN_PORT))
    sock.settimeout(1)  # ca Ctrl+C să meargă imediat și pe Windows
    print(f"Ascult pe {config.LISTEN_HOST}:{config.LISTEN_PORT}")
    while True:
        try:
            data, client = sock.recvfrom(4096)
        except TimeoutError:
            continue
        start = time.perf_counter()
        try:
            reply_data, action, domain, qtype = handle_query(data)
            sock.sendto(reply_data, client)
            ms = (time.perf_counter() - start) * 1000
            print(f"{client[0]} {qtype} {domain} {action} {ms:.1f}ms")
        except Exception as e:  # noqa: BLE001
            print("Eroare:", e)


if __name__ == "__main__":
    main()
