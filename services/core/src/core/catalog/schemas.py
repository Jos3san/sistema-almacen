"""Request and response bodies of the catalog API (docs/09)."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
UpperCode = Annotated[
    str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=1, max_length=30)
]
# Manufacturer barcodes are usually EAN (digits); internal ones may use letters too.
Barcode = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9A-Za-z-]{4,32}$")]
Money = Annotated[Decimal, Field(max_digits=12, decimal_places=2)]


class _In(BaseModel):
    """Request bodies reject unknown fields (e.g. "factor" when editing a presentation).

    Silently ignoring them would hide mistakes and opens the door to mass assignment.
    """

    model_config = ConfigDict(extra="forbid")


class _Out(BaseModel):
    """Response models are read straight from the database objects."""

    model_config = ConfigDict(from_attributes=True)


# ---------- categories and brands ----------


class NamedCreate(_In):
    """New category or brand."""

    name: Name


class NamedUpdate(_In):
    """Change the name or deactivate a category or brand."""

    name: Name | None = None
    active: bool | None = None


class NamedOut(_Out):
    """A category or brand."""

    id: int
    name: str
    active: bool


# ---------- locations ----------


class LocationCreate(_In):
    """New store or warehouse."""

    name: Name
    type: Literal["STORE", "WAREHOUSE"]
    address: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None


class LocationUpdate(_In):
    """Change a location; its type does not change."""

    name: Name | None = None
    address: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None
    active: bool | None = None


class LocationOut(_Out):
    """A location."""

    id: int
    name: str
    type: str
    address: str | None
    active: bool


# ---------- products, presentations and prices ----------


class PriceTierIn(_In):
    """Price of one presentation from min_quantity on, VAT included."""

    min_quantity: int = Field(ge=1)
    price: Money = Field(gt=0)


class PriceTiersReplace(_In):
    """The full list of tiers of a presentation; it replaces the previous one."""

    tiers: list[PriceTierIn] = Field(min_length=1, max_length=20)

    @field_validator("tiers")
    @classmethod
    def _starts_at_one_and_no_repeats(cls, tiers: list[PriceTierIn]) -> list[PriceTierIn]:
        """There must be a price from 1 (docs/03 rule 6) and no repeated quantity."""
        quantities = [tier.min_quantity for tier in tiers]
        if 1 not in quantities:
            raise ValueError("There must be a price from quantity 1")
        if len(set(quantities)) != len(quantities):
            raise ValueError("Each min_quantity can appear only once")
        return sorted(tiers, key=lambda tier: tier.min_quantity)


class PriceTierOut(_Out):
    """A price tier."""

    min_quantity: int
    price: Decimal


class PresentationCreate(_In):
    """New way to sell a product (CAJA, DOCENA...). The factor cannot change later."""

    name: UpperCode
    factor: int = Field(ge=1, le=100_000)
    barcode: Barcode | None = None


class PresentationUpdate(_In):
    """Rename, change the barcode or deactivate a presentation (never its factor)."""

    name: UpperCode | None = None
    barcode: Barcode | None = None
    active: bool | None = None


class PresentationOut(_Out):
    """A presentation with its prices."""

    id: int
    name: str
    factor: int
    barcode: str | None
    active: bool
    price_tiers: list[PriceTierOut]


class ProductCreate(_In):
    """New product. Its base presentation (factor 1) is created with it."""

    sku: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
    barcode: Barcode | None = None
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    category_id: int
    brand_id: int | None = None
    base_unit: Annotated[
        str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=1, max_length=20)
    ]
    cost: Money | None = Field(default=None, ge=0)


class ProductUpdate(_In):
    """Change a product. SKU and base unit do not change: they identify it and its stock."""

    barcode: Barcode | None = None
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ] | None = None  # fmt: skip
    category_id: int | None = None
    brand_id: int | None = None
    cost: Money | None = Field(default=None, ge=0)
    active: bool | None = None


class ProductOut(_Out):
    """A product with its presentations and prices. cost appears only with cost.view."""

    id: int
    sku: str
    barcode: str | None
    name: str
    category: NamedOut
    brand: NamedOut | None
    base_unit: str
    cost: Decimal | None = None
    active: bool
    presentations: list[PresentationOut]


class ProductPage(BaseModel):
    """One page of a product search."""

    items: list[dict]
    total: int


class MinimumStockIn(_In):
    """Alert threshold in base units (0 means no alert)."""

    quantity: int = Field(ge=0, le=10_000_000)
