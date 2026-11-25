import socket
from dnslib import DNSRecord
import config


def forward(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    try:
        s.sendto(data, (config.UPSTREAM_HOST, config.UPSTREAM_PORT))
        reply, _ = s.recvfrom(4096)
        return reply
    finally:
        s.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.LISTEN_HOST, config.LISTEN_PORT))
    print(f"Ascult pe {config.LISTEN_HOST}:{config.LISTEN_PORT}")
    while True:
        data, client = sock.recvfrom(4096)
        try:
            req = DNSRecord.parse(data)
            domain = str(req.q.qname).rstrip(".").lower()
            print(f"{client[0]} -> {domain}")
            sock.sendto(forward(data), client)
        except Exception as e:
            print("Eroare:", e)


if __name__ == "__main__":
    main()