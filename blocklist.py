"""Blocklist: incarcare liste in format hosts si verificare domenii."""

_blocked = set()
whitelist = set() #domenii permise

#intrari din hosts care nu sunt reclame
_IGNORED = {
    "localhost", "localhost.localdomain", "local", "broadcasthost", "0.0.0.0",
}

def _normalize(domain):
    return domain.strip().lower().rstrip(".")

def load(path):
    """Citeste fisierul hosts si intoarce nr de domenii incarcate"""
    _blocked.clear()
    with open(path, encoding="utf-8") as f:
        for line in f:
           line = line.split("#", 1)[0].strip()
           if not line:
                continue
           parts = line.split()
           if len(parts) < 2 or parts[0] not in ("0.0.0.0", "127.0.0.1"):
                continue
           domain = _normalize(parts[1])
           if domain not in _IGNORED:
                _blocked.add(domain)
    return len(_blocked)

def _candidates(domain):
    """x.y.ads.com -> x.y.ads.com, y.ads.com, ads.com, com"""
    labels = domain.split(".")
    for i in range(len(labels)):
        yield ".".join(labels[i:])

def is_blocked(domain):
    """True daca domeniul sau un domeniu-parinte este in blocklist"""
    domain = _normalize(domain)
    candidates = list(_candidates(domain))
    if any(c in whitelist for c in candidates):
        return False
    return any(c in _blocked for c in candidates)