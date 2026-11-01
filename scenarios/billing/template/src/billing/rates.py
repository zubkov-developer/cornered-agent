"""VAT rates (percent) by the customer's country.

The seller is established in Germany. B2C sales to other EU countries are
taxed at the customer's country rate (OSS).
"""

from decimal import Decimal

SELLER_COUNTRY = "DE"
EU_COUNTRIES = {"DE", "FR", "NL", "AT", "IT", "ES"}

VAT_RATES = {
    "DE": {"standard": Decimal("19"), "reduced": Decimal("7")},
    "FR": {"standard": Decimal("20"), "reduced": Decimal("5")},
    "NL": {"standard": Decimal("21"), "reduced": Decimal("9")},
    "AT": {"standard": Decimal("20"), "reduced": Decimal("10")},
    "IT": {"standard": Decimal("22"), "reduced": Decimal("10")},
    "ES": {"standard": Decimal("21"), "reduced": Decimal("10")},
}


def vat_rate(country, category="standard"):
    return VAT_RATES[country][category]
