#!/usr/bin/env python3
"""ETL job: source {"customers": [...]} -> destination {"clienti": {"<id>": {...}}}.

Reads one JSON value (object or array of objects) from stdin and writes one
JSON value of the same shape to stdout.
"""
import json
import sys

# Destination "stato" is a string, source "active" is a boolean.
# Best-effort mapping (low confidence): there is no source field named like
# "stato", so we infer it from "active": True -> "attivo", False -> "inattivo".
STATO_ACTIVE = "attivo"
STATO_INACTIVE = "inattivo"


def transform_customer(customer):
    """Transform one source customer into its destination entry (without key)."""
    # nome_completo: "full name" = firstName + lastName (name similarity).
    nome_completo = f"{customer['firstName']} {customer['lastName']}".strip()
    return {
        "nome_completo": nome_completo,
        "contatti": {"email": customer["email"]},
        "citta": customer["city"],  # city -> citta (Italian translation of name)
        # stato: best-effort, derived from boolean "active" (see note above).
        "stato": STATO_ACTIVE if customer["active"] else STATO_INACTIVE,
    }


def transform(record):
    """Transform one source object ({"customers": [...]}) to destination shape."""
    clienti = {}
    for customer in record.get("customers") or []:
        # The destination is an object keyed by customer id (as a string);
        # the keys "1", "2", "3" in the schema are treated as id-keyed entries.
        # If an id repeats, the later record wins.
        clienti[str(customer["id"])] = transform_customer(customer)
    return {"clienti": clienti}


def run(data):
    """Handle a single object or an array of objects, preserving the shape."""
    if isinstance(data, list):
        return [transform(item) for item in data]
    return transform(data)


def main():
    data = json.load(sys.stdin)
    json.dump(run(data), sys.stdout)


if __name__ == "__main__":
    main()