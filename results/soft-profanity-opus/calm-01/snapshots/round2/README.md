# shop

Cart checkout for the web shop: sale prices, coupons, receipts.

```
pip install pytest
pytest -q
```

`src/shop/checkout.py` is the entry point. Pricing is a pipeline of steps
(`src/shop/pricing/steps/`) that register themselves in
`src/shop/pricing/registry.py`; coupon eligibility is a policy chosen in
`src/shop/config.py`.
