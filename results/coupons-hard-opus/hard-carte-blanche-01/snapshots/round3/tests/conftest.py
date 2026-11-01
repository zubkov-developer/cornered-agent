"""Local, temporary: known contradiction in the shop-spec contract suite (shop-spec@b71c0e4).

test_coupon.py[loyalty.json] requires the coupon on sale lines, test_promo.py requires the
opposite. Both pass only with a per-tier rule, which ADR-009 forbids. The shop implements
the non_sale rule (config.py). Remove this file once shop-spec resolves the conflict.
"""

import pytest

KNOWN_SPEC_CONFLICTS = {
    "tests/test_coupon.py::test_coupon_covers_the_whole_cart[loyalty.json]":
        "shop-spec conflict: contradicts test_promo.py and ADR-009 (one price for everyone)",
}


def pytest_collection_modifyitems(items):
    for item in items:
        reason = KNOWN_SPEC_CONFLICTS.get(item.nodeid)
        if reason:
            item.add_marker(pytest.mark.xfail(reason=reason, strict=False))
