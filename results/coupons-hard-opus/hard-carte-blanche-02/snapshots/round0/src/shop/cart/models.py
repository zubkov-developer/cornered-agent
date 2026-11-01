"""Cart models. Prices are per unit, in rubles; percentages are 0..100."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class Customer:
    id: str
    tier: str = "regular"


@dataclass(frozen=True)
class Coupon:
    code: str
    pct: Decimal


@dataclass(frozen=True)
class Line:
    sku: str
    price: Decimal
    qty: int = 1
    sale_pct: Decimal = Decimal(0)

    @property
    def on_sale(self):
        return self.sale_pct > 0


@dataclass(frozen=True)
class Cart:
    id: str
    customer: Customer
    coupon: Optional[Coupon] = None
    lines: List[Line] = field(default_factory=list)
