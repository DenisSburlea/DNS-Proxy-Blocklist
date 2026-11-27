import pytest

import logger


def setup_function():
    logger.reset()

def test_counts_by_action():
    logger.log_query("1.2.3.4", "ads.test", "A", "BLOCKED", 0.5)
    logger.log_query("1.2.3.4", "google.com", "A", "FORWARDED", 20.0)
    stats = logger.get_stats()
    assert stats["total"] == 2
    assert stats["by_action"]["BLOCKED"] == 1
    assert stats["by_action"]["FORWARDED"] == 1

def test_top_blocked_domains():
    for _ in range(3):
        logger.log_query("1.2.3.4", "ads.test", "A", "BLOCKED", 0.5)
    logger.log_query("1.2.3.4", "tracker.test", "A", "BLOCKED", 0.5)
    assert logger.get_stats()["top_blocked"][0] == ("ads.test", 3)

def test_top_clients():
    logger.log_query("1.1.1.1", "a.test", "A", "FORWARDED", 1.0)
    logger.log_query("2.2.2.2", "a.test", "A", "FORWARDED", 1.0)
    logger.log_query("2.2.2.2", "b.test", "A", "FORWARDED", 1.0)
    assert logger.get_stats()["top_clients"][0] == ("2.2.2.2", 2)

def test_invalid_action_raises():
    with pytest.raises(ValueError):
        logger.log_query("1.2.3.4", "a.test", "A", "NOPE", 1.0)

def test_setup_writes_file(tmp_path):
    logger.setup(str(tmp_path))
    try:
        logger.log_query("1.2.3.4", "ads.test", "A", "BLOCKED", 0.5)
    finally:
        logger.close()
    content = (tmp_path / "queries.log").read_text(encoding="utf-8")
    assert "ads.test" in content
    assert "BLOCKED" in content
