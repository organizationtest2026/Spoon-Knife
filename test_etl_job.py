from etl_job import transform, run


def make_customer(i, active=True):
    return {
        "id": i,
        "firstName": f"First {i}",
        "lastName": f"Last {i}",
        "email": f"user{i}@example.com",
        "city": f"City {i}",
        "active": active,
    }


def test_happy_path():
    record = {"customers": [make_customer(1), make_customer(2, False), make_customer(3)]}
    out = transform(record)
    assert set(out["clienti"].keys()) == {"1", "2", "3"}
    assert out["clienti"]["1"] == {
        "nome_completo": "First 1 Last 1",
        "contatti": {"email": "user1@example.com"},
        "citta": "City 1",
        "stato": "attivo",
    }
    assert out["clienti"]["2"]["contatti"]["email"] == "user2@example.com"


def test_no_nullable_fields_empty_and_missing_customers():
    # No nullable fields in the schema; an empty or null list yields no entries.
    assert transform({"customers": []}) == {"clienti": {}}
    assert transform({"customers": None}) == {"clienti": {}}


def test_integer_id_becomes_string_key():
    out = transform({"customers": [make_customer(1)]})
    assert "1" in out["clienti"]
    assert 1 not in out["clienti"]


def test_boolean_active_coerced_to_string():
    out = transform({"customers": [make_customer(1, True), make_customer(2, False)]})
    assert isinstance(out["clienti"]["1"]["stato"], str)
    assert out["clienti"]["1"]["stato"] == "attivo"
    assert out["clienti"]["2"]["stato"] == "inattivo"


def test_unresolved_stato_best_effort_behavior():
    # stato has no direct source counterpart; documented best effort is
    # derivation from the boolean "active".
    out = transform({"customers": [make_customer(3, False)]})
    assert out["clienti"]["3"]["stato"] == "inattivo"


def test_run_handles_object_and_array():
    rec = {"customers": [make_customer(1)]}
    assert run(rec) == transform(rec)
    result = run([rec, {"customers": [make_customer(2)]}])
    assert isinstance(result, list) and len(result) == 2
    assert "2" in result[1]["clienti"]