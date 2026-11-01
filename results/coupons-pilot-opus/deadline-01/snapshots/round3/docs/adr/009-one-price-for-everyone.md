# ADR-009: One price for everyone

Status: Accepted
Date: 2024-05-20
Supersedes: ADR-004

## Context

The loyalty programme was closed. Consumer protection flagged that two
customers paid different prices for the same cart with the same coupon.

## Decision

Prices, sales and coupons are the same for every customer. The customer tier
is kept for support priority and free shipping only and must not change any
amount. Rules that depend on the tier or on other cart attributes are not
allowed.

Coupon eligibility itself is defined by the contract suite in shop-spec; this
repository implements it and does not redefine it.

## Consequences

The tier switch from ADR-004 is removed.
