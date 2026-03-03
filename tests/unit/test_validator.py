from app.services.ai.validator import validate_sql


def test_valid_select():
    ok, err = validate_sql("SELECT * FROM flights LIMIT 10")
    assert ok is True

def test_rejects_delete():
    ok, err = validate_sql("DELETE FROM flights")
    assert ok is False

def test_rejects_drop():
    ok, err = validate_sql("DROP TABLE flights")
    assert ok is False

def test_rejects_empty():
    ok, err = validate_sql("")
    assert ok is False
