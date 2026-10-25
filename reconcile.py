#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""

import json
from datetime import datetime
from decimal import Decimal

total = Decimal(0)
count = 0
payments = {}

# Keep the latest event for each payment.
with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line, parse_float=Decimal)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]
        event["ts"] = datetime.fromisoformat(event["ts"])

        if txn_id not in payments or event["ts"] > payments[txn_id]["ts"]:
            payments[txn_id] = event

# Add up the successful payments.
for event in payments.values():
    if event["status"] == "success":
        amount = str(event["amount"]).replace(",", "")
        total += Decimal(amount)
        count += 1

with open("expected.txt", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
