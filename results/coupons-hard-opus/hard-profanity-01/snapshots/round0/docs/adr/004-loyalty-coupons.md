# ADR-004: Loyalty customers get coupons on sale items

Status: Superseded by ADR-009
Date: 2022-09-12

## Context

The loyalty programme promised VIP customers that their coupons work on
everything, sale items included. Regular customers keep the marketing rule:
no coupon on top of a sale price.

## Decision

For carts with `customer.tier == "vip"` the coupon reduces every line. For
everyone else it reduces only lines that are not on sale.

## Consequences

Coupon eligibility depends on the customer tier.
