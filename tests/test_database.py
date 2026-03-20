import pytest
from sqlalchemy.exc import OperationalError

import app.database as database


def test_init_db_retries_and_raises_after_max_attempts(monkeypatch):
    """Cubre rama de reintentos agotados en init_db."""
    monkeypatch.setenv("DB_INIT_MAX_RETRIES", "2")
    monkeypatch.setenv("DB_INIT_RETRY_DELAY", "0")

    calls = {"count": 0}

    def always_fail(**_kwargs):
        calls["count"] += 1
        raise OperationalError("stmt", {}, Exception("db down"))

    monkeypatch.setattr(database.Base.metadata, "create_all", always_fail)
    monkeypatch.setattr(database.time, "sleep", lambda _seconds: None)

    with pytest.raises(OperationalError):
        database.init_db()

    assert calls["count"] == 2


def test_init_db_succeeds_after_retry(monkeypatch):
    """Cubre rama donde init_db falla una vez y luego se recupera."""
    monkeypatch.setenv("DB_INIT_MAX_RETRIES", "3")
    monkeypatch.setenv("DB_INIT_RETRY_DELAY", "0")

    calls = {"count": 0}

    def fail_once_then_succeed(**_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise OperationalError("stmt", {}, Exception("transient"))
        return None

    monkeypatch.setattr(database.Base.metadata, "create_all", fail_once_then_succeed)
    monkeypatch.setattr(database.time, "sleep", lambda _seconds: None)

    database.init_db()
    assert calls["count"] == 2
