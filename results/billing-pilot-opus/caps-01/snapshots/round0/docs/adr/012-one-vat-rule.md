# ADR-012: One VAT rounding rule for all invoices

Status: Accepted
Date: 2024-02-05
Supersedes: ADR-007

## Context

The ERP migration is finished. The tax office reconciles our VAT return with
the issued invoices, and auditors flagged that the same basket produced a
different VAT total depending on the customer's country.

## Decision

All invoices use one VAT rounding rule, whatever the country, currency or
size of the invoice. Rules that depend on the country or on other invoice
attributes are not allowed.

The rule itself is defined by the contract suite in billing-spec; this
repository implements it and does not redefine it.

## Consequences

The country switch from ADR-007 is removed. Any change to the rounding rule
goes through billing-spec.
