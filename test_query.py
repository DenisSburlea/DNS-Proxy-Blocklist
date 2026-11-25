from dnslib import DNSRecord

q = DNSRecord.question("google.com")
raw = q.send("127.0.0.1", 5300, timeout=10)
print(DNSRecord.parse(raw))