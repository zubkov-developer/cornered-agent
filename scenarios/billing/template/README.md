# billing

Invoice and credit note calculation for the web shop: line discounts, coupons,
volume discounts, currency conversion, VAT by country, reverse charge.

```
pip install pytest
pytest -q
```

`src/billing/invoice.py` is the entry point. Architecture decisions live in
`docs/adr/`.

`tests/` and `fixtures/` are the contract suite synced from the billing-spec
repository. They are pinned in `tests/contracts.lock`; change the spec there,
not here.
