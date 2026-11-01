"""Local overrides for the contract suite synced from shop-spec.

KNOWN SPEC CONFLICT (temporary, remove once shop-spec is fixed):
test_promo.py says a coupon skips sale lines, test_coupon.py[loyalty.json]
says it covers them. The fixtures differ only by customer tier, so passing both
needs a tier-dependent price, which ADR-009 forbids. The shop keeps the current
rule (config.py: coupon_scope = "non_sale") and the conflicting case is marked
as an expected failure until shop-spec decides. strict=True: if the spec or the
policy changes so the case passes, this marker fails loudly and must be removed.
"""

import pytest

KNOWN_SPEC_CONFLICTS = {
    "tests/test_coupon.py::test_coupon_covers_the_whole_cart[loyalty.json]":
        "shop-spec conflict: coupon on sale lines (test_coupon vs test_promo), see tests/conftest.py",
}


def pytest_collection_modifyitems(items):
    for item in items:
        reason = KNOWN_SPEC_CONFLICTS.get(item.nodeid)
        if reason:
            item.add_marker(pytest.mark.xfail(reason=reason, strict=True))
