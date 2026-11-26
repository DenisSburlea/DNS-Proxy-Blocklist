import blocklist

HOSTS = """# comentariu
127.0.0.1 localhost
0.0.0.0 0.0.0.0

0.0.0.0 ads.example.com
0.0.0.0 tracker.test # comentariu pe linie
"""

def make_list(tmp_path):
    f = tmp_path / "hosts.txt"
    f.write_text(HOSTS, encoding="utf-8")
    blocklist.whitelist.clear()
    return blocklist.load(str(f))

def test_load_ignores_comments_and_localhosts(tmp_path):
    assert make_list(tmp_path) == 2


def test_blocked_domains(tmp_path):
    make_list(tmp_path)
    assert blocklist.is_blocked("ads.example.com") is True

def test_subdomain_of_blocked_domain(tmp_path):
    make_list(tmp_path)
    assert blocklist.is_blocked("x.y.ads.example.com") is True

def test_parent_of_blocked_domain_is_allowed(tmp_path):
    make_list(tmp_path)
    assert blocklist.is_blocked("example.com") is False

def test_unknown_domain_is_allowed(tmp_path):
    make_list(tmp_path)
    assert blocklist.is_blocked("google.com") is False

def test_case_and_trailing_dot(tmp_path):
    make_list(tmp_path)
    assert blocklist.is_blocked("ADS.Example.com.") is True

def test_whitelist_wins(tmp_path):
    make_list(tmp_path)
    blocklist.whitelist.add("ads.example.com")
    assert blocklist.is_blocked("ads.example.com") is False
    assert blocklist.is_blocked("x.ads.example.com") is False

def load_text(tmp_path, text):
    f = tmp_path / "hosts.txt"
    f.write_text(text, encoding="utf-8")
    blocklist.whitelist.clear()
    return blocklist.load(str(f))


def test_127_lines_are_blocked_too(tmp_path):
    load_text(tmp_path, "127.0.0.1 evil.test\n")
    assert blocklist.is_blocked("evil.test") is True


def test_lines_with_other_ips_are_ignored(tmp_path):
    assert load_text(tmp_path, "192.168.1.1 router.test\n") == 0
    assert blocklist.is_blocked("router.test") is False


def test_duplicates_are_counted_once(tmp_path):
    assert load_text(tmp_path, "0.0.0.0 a.test\n0.0.0.0 a.test\n") == 1


def test_reload_clears_old_entries(tmp_path):
    load_text(tmp_path, "0.0.0.0 old.test\n")
    load_text(tmp_path, "0.0.0.0 new.test\n")
    assert blocklist.is_blocked("old.test") is False
    assert blocklist.is_blocked("new.test") is True


def test_empty_domain_is_allowed(tmp_path):
    load_text(tmp_path, "0.0.0.0 a.test\n")
    assert blocklist.is_blocked("") is False


def test_whitelist_for_one_subdomain_only(tmp_path):
    load_text(tmp_path, "0.0.0.0 ads.example.com\n")
    blocklist.whitelist.add("ok.ads.example.com")
    assert blocklist.is_blocked("ok.ads.example.com") is False
    assert blocklist.is_blocked("ads.example.com") is True
    assert blocklist.is_blocked("other.ads.example.com") is True