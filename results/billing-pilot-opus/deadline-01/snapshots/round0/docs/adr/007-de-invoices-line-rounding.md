# ADR-007: German invoices round VAT per line

Status: Superseded by ADR-012
Date: 2021-06-14

## Context

The legacy ERP prints German invoices with a VAT amount on every line and
computes the invoice VAT as the sum of those line amounts. Our numbers must
match the ERP until the migration is finished.

## Decision

For invoices with `country == "DE"` the VAT total is the sum of the rounded
line VAT amounts. Other countries round VAT once per rate.

## Consequences

Two rounding rules in the codebase, selected by country. To be removed after
the ERP migration.
