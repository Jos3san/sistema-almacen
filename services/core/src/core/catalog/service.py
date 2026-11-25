"""Business rules of the catalog (docs/09). Knows nothing about HTTP (docs/06 D1.11).

Every change runs in one transaction together with its audit entry: both are
saved or neither is.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from almacen_security import TokenClaims
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.audit import service as audit
from core.catalog import repository as repo
from core.catalog.models import (
    Brand,
    Category,
    Location,
    MinimumStock,
    Presentation,
    PriceTier,
    Product,
)
from core.catalog.schemas import (
    LocationCreate,
    LocationUpdate,
    NamedCreate,
    NamedUpdate,
    PresentationCreate,
    PresentationUpdate,
    PriceTierIn,
    ProductCreate,
    ProductUpdate,
)
from core.errors import BusinessRuleError, ConflictError, NotFoundError

NAMED_ENTITIES: dict[str, type[Category] | type[Brand]] = {"category": Category, "brand": Brand}


@contextmanager
def _transaction(session: Session) -> Iterator[None]:
    """Run a change in one transaction; a uniqueness clash at commit becomes a 409.

    The services check duplicates first to give clear messages; this catches the
    rare case of two people saving the same value at the same moment.
    """
    try:
        with session.begin():
            yield
    except IntegrityError as error:
        raise ConflictError("The change conflicts with existing data") from error


def _changes(data: BaseModel, required: set[str]) -> dict[str, Any]:
    """Fields sent in a PATCH (even when null); required fields cannot be cleared."""
    changes = {name: getattr(data, name) for name in data.model_fields_set}
    cleared = [name for name in required if name in changes and changes[name] is None]
    if cleared:
        raise BusinessRuleError(f"These fields cannot be empty: {', '.join(cleared)}")
    return changes


def _snapshot(record: object, fields: list[str]) -> dict[str, Any]:
    """The values of some fields, as JSON-friendly data for the audit log (Decimal → text)."""
    snapshot: dict[str, Any] = {}
    for name in fields:
        value = getattr(record, name)
        is_plain = value is None or isinstance(value, bool | int | str)
        snapshot[name] = value if is_plain else str(value)
    return snapshot


# ---------- categories and brands ----------


def create_named(session: Session, user: TokenClaims, entity: str, data: NamedCreate):
    """Create a category or brand with a name not used before."""
    model = NAMED_ENTITIES[entity]
    with _transaction(session):
        if repo.name_taken(session, model, data.name, exclude_id=None):
            raise ConflictError(f"A {entity} with that name already exists")
        record = model(name=data.name)
        session.add(record)
        session.flush()
        audit.record(
            session, user, f"{entity}.create", entity, record.id, after={"name": data.name}
        )
    return record


def update_named(
    session: Session, user: TokenClaims, entity: str, record_id: int, data: NamedUpdate
):
    """Rename or (de)activate a category or brand."""
    model = NAMED_ENTITIES[entity]
    changes = _changes(data, required={"name", "active"})
    with _transaction(session):
        record = session.get(model, record_id)
        if record is None:
            raise NotFoundError(f"The {entity} does not exist")
        if "name" in changes and repo.name_taken(session, model, changes["name"], record_id):
            raise ConflictError(f"A {entity} with that name already exists")
        before = _snapshot(record, ["name", "active"])
        for name, value in changes.items():
            setattr(record, name, value)
        audit.record(
            session,
            user,
            f"{entity}.update",
            entity,
            record_id,
            before,
            _snapshot(record, ["name", "active"]),
        )
    return record


# ---------- locations ----------

_LOCATION_FIELDS = ["name", "type", "address", "active"]


def create_location(session: Session, user: TokenClaims, data: LocationCreate) -> Location:
    """Create a store or warehouse with a unique name."""
    with _transaction(session):
        if repo.name_taken(session, Location, data.name, exclude_id=None):
            raise ConflictError("A location with that name already exists")
        location = Location(name=data.name, type=data.type, address=data.address)
        session.add(location)
        session.flush()
        audit.record(
            session, user, "location.create", "location", location.id,
            after=_snapshot(location, _LOCATION_FIELDS),
        )  # fmt: skip
    return location


def update_location(
    session: Session, user: TokenClaims, location_id: int, data: LocationUpdate
) -> Location:
    """Rename, change the address or (de)activate a location."""
    changes = _changes(data, required={"name", "active"})
    with _transaction(session):
        location = session.get(Location, location_id)
        if location is None:
            raise NotFoundError("The location does not exist")
        if "name" in changes and repo.name_taken(session, Location, changes["name"], location_id):
            raise ConflictError("A location with that name already exists")
        before = _snapshot(location, _LOCATION_FIELDS)
        for name, value in changes.items():
            setattr(location, name, value)
        audit.record(
            session, user, "location.update", "location", location_id,
            before, _snapshot(location, _LOCATION_FIELDS),
        )  # fmt: skip
    return location


# ---------- products ----------

_PRODUCT_FIELDS = [
    "sku",
    "barcode",
    "name",
    "category_id",
    "brand_id",
    "base_unit",
    "cost",
    "active",
]


def _check_references(session: Session, category_id: int | None, brand_id: int | None) -> None:
    """The category and brand must exist and be active."""
    if category_id is not None:
        category = session.get(Category, category_id)
        if category is None or not category.active:
            raise BusinessRuleError("The category does not exist or is inactive")
    if brand_id is not None:
        brand = session.get(Brand, brand_id)
        if brand is None or not brand.active:
            raise BusinessRuleError("The brand does not exist or is inactive")


def create_product(session: Session, user: TokenClaims, data: ProductCreate) -> Product:
    """Create a product and, with it, its base presentation (factor 1, docs/09)."""
    with _transaction(session):
        if repo.sku_taken(session, data.sku):
            raise ConflictError("A product with that SKU already exists")
        if data.barcode and repo.barcode_taken(session, data.barcode):
            raise ConflictError("That barcode is already used")
        _check_references(session, data.category_id, data.brand_id)
        product = Product(**data.model_dump())
        session.add(product)
        session.flush()
        session.add(Presentation(product_id=product.id, name=product.base_unit, factor=1))
        audit.record(
            session, user, "product.create", "product", product.id,
            after=_snapshot(product, _PRODUCT_FIELDS),
        )  # fmt: skip
    return repo.get_product(session, product.id)


def update_product(
    session: Session, user: TokenClaims, product_id: int, data: ProductUpdate
) -> Product:
    """Change a product's data, cost or status (SKU and base unit never change)."""
    changes = _changes(data, required={"name", "category_id", "active"})
    with _transaction(session):
        product = session.get(Product, product_id)
        if product is None:
            raise NotFoundError("The product does not exist")
        if changes.get("barcode") and repo.barcode_taken(
            session, changes["barcode"], exclude_product_id=product_id
        ):
            raise ConflictError("That barcode is already used")
        _check_references(session, changes.get("category_id"), changes.get("brand_id"))
        before = _snapshot(product, _PRODUCT_FIELDS)
        for name, value in changes.items():
            setattr(product, name, value)
        audit.record(
            session, user, "product.update", "product", product_id,
            before, _snapshot(product, _PRODUCT_FIELDS),
        )  # fmt: skip
    session.expire_all()
    return repo.get_product(session, product_id)


# ---------- presentations and prices ----------

_PRESENTATION_FIELDS = ["product_id", "name", "factor", "barcode", "active"]


def add_presentation(
    session: Session, user: TokenClaims, product_id: int, data: PresentationCreate
) -> Product:
    """Add a way to sell the product (CAJA de 12, DOCENA...)."""
    with _transaction(session):
        if session.get(Product, product_id) is None:
            raise NotFoundError("The product does not exist")
        if repo.presentation_name_taken(session, product_id, data.name):
            raise ConflictError("The product already has a presentation with that name")
        if data.barcode and repo.barcode_taken(session, data.barcode):
            raise ConflictError("That barcode is already used")
        presentation = Presentation(product_id=product_id, **data.model_dump())
        session.add(presentation)
        session.flush()
        audit.record(
            session, user, "presentation.create", "presentation", presentation.id,
            after=_snapshot(presentation, _PRESENTATION_FIELDS),
        )  # fmt: skip
    session.expire_all()
    return repo.get_product(session, product_id)


def update_presentation(
    session: Session, user: TokenClaims, presentation_id: int, data: PresentationUpdate
) -> Product:
    """Rename, change the barcode or (de)activate a presentation. Its factor never changes."""
    changes = _changes(data, required={"name", "active"})
    with _transaction(session):
        presentation = repo.get_presentation(session, presentation_id)
        if presentation is None:
            raise NotFoundError("The presentation does not exist")
        if (
            changes.get("active") is False
            and presentation.factor == 1
            and presentation.product.active
        ):
            raise BusinessRuleError(
                "The base presentation (factor 1) cannot be deactivated while the product is active"
            )
        if "name" in changes and repo.presentation_name_taken(
            session, presentation.product_id, changes["name"], exclude_id=presentation_id
        ):
            raise ConflictError("The product already has a presentation with that name")
        if changes.get("barcode") and repo.barcode_taken(
            session, changes["barcode"], exclude_presentation_id=presentation_id
        ):
            raise ConflictError("That barcode is already used")
        before = _snapshot(presentation, _PRESENTATION_FIELDS)
        for name, value in changes.items():
            setattr(presentation, name, value)
        audit.record(
            session, user, "presentation.update", "presentation", presentation_id,
            before, _snapshot(presentation, _PRESENTATION_FIELDS),
        )  # fmt: skip
    session.expire_all()
    return repo.get_product(session, presentation.product_id)


def replace_price_tiers(
    session: Session, user: TokenClaims, presentation_id: int, tiers: list[PriceTierIn]
) -> Product:
    """Replace every price tier of a presentation; the old and new prices go to the audit log."""
    with _transaction(session):
        presentation = repo.get_presentation(session, presentation_id)
        if presentation is None:
            raise NotFoundError("The presentation does not exist")
        before = {"tiers": [[t.min_quantity, str(t.price)] for t in presentation.price_tiers]}
        presentation.price_tiers.clear()
        session.flush()
        presentation.price_tiers.extend(
            PriceTier(min_quantity=tier.min_quantity, price=tier.price) for tier in tiers
        )
        after = {"tiers": [[t.min_quantity, str(t.price)] for t in tiers]}
        audit.record(
            session, user, "price_tiers.replace", "presentation", presentation_id, before, after
        )
    session.expire_all()
    return repo.get_product(session, presentation.product_id)


# ---------- minimum stock ----------


def set_minimum_stock(
    session: Session, user: TokenClaims, product_id: int, location_id: int, quantity: int
) -> None:
    """Set the alert threshold of a product in a location (0 = no alert)."""
    with _transaction(session):
        if session.get(Product, product_id) is None:
            raise NotFoundError("The product does not exist")
        location = session.get(Location, location_id)
        if location is None or not location.active:
            raise NotFoundError("The location does not exist or is inactive")
        current = repo.get_minimum_stock(session, product_id, location_id)
        before = {"quantity": current.quantity} if current else None
        if current is None:
            session.add(
                MinimumStock(product_id=product_id, location_id=location_id, quantity=quantity)
            )
        else:
            current.quantity = quantity
        audit.record(
            session, user, "minimum_stock.set", "product", product_id,
            before, {"location_id": location_id, "quantity": quantity},
        )  # fmt: skip
