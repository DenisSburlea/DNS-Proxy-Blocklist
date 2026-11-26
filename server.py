import socket

from dnslib import RCODE, DNSRecord

import config
import resolver


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.LISTEN_HOST, config.LISTEN_PORT))
    sock.settimeout(1)
    print(f"Ascult pe {config.LISTEN_HOST}:{config.LISTEN_PORT}")
    while True:
        try:
            data, client = sock.recvfrom(4096)
        except TimeoutError:
            continue
        try:
            req = DNSRecord.parse(data)
            domain = str(req.q.qname).rstrip(".").lower()
            print(f"{client[0]} -> {domain}")
            reply_data = resolver.forward(data)
            if reply_data is None:
                reply = req.reply()
                reply.header.rcode = RCODE.SERVFAIL
                reply_data = reply.pack()
            sock.sendto(reply_data, client)
        except Exception as e:  # noqa: BLE001 - serverul nu trebuie sa cada la pachete malformate
            print("Eroare:", e)


if __name__ == "__main__":
    main()