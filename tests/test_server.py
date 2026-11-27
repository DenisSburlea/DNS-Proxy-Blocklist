from dnslib import RCODE, DNSRecord

import blocklist
import resolver
import server


def make_query(domain):
    return DNSRecord.question(domain).pack()


def test_blocked_domain_gets_nxdomain(monkeypatch):
    monkeypatch.setattr(blocklist, "is_blocked", lambda d: True)
    reply, action, _, _ = server.handle_query(make_query("ads.test"))
    assert action == "BLOCKED"
    assert DNSRecord.parse(reply).header.rcode == RCODE.NXDOMAIN


def test_allowed_domain_is_forwarded(monkeypatch):
    monkeypatch.setattr(blocklist, "is_blocked", lambda d: False)
    fake = DNSRecord.question("ok.test").reply().pack()
    monkeypatch.setattr(resolver, "forward", lambda data: fake)
    reply, action, _, _ = server.handle_query(make_query("ok.test"))
    assert action == "FORWARDED"
    assert reply == fake


def test_upstream_failure_gives_servfail(monkeypatch):
    monkeypatch.setattr(blocklist, "is_blocked", lambda d: False)
    monkeypatch.setattr(resolver, "forward", lambda data: None)
    reply, action, _, _ = server.handle_query(make_query("ok.test"))
    assert action == "FAILED"
    assert DNSRecord.parse(reply).header.rcode == RCODE.SERVFAIL
