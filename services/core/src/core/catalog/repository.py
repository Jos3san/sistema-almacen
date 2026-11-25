"""Database queries of the catalog. No business rules here (docs/06 D1.11)."""

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session, selectinload

from core.catalog.models import (
    Brand,
    Category,
    Location,
    MinimumStock,
    Presentation,
    Product,
)

NamedModel = type[Category] | type[Brand] | type[Location]


def list_all(session: Session, model: NamedModel, only_active: bool) -> list:
    """All categories, brands or locations, sorted by name."""
    query = select(model).order_by(func.lower(model.name))
    if only_active:
        query = query.where(model.active.is_(True))
    return list(session.scalars(query))


def name_taken(session: Session, model: NamedModel, name: str, exclude_id: int | None) -> bool:
    """Tell whether another row already uses this name (case-insensitive)."""
    query = select(model.id).where(func.lower(model.name) == name.lower())
    if exclude_id is not None:
        query = query.where(model.id != exclude_id)
    return session.scalar(query.limit(1)) is not None


def sku_taken(session: Session, sku: str) -> bool:
    """Tell whether a product already uses this SKU (case-insensitive)."""
    return session.scalar(select(exists().where(func.lower(Product.sku) == sku.lower())))


def barcode_taken(
    session: Session,
    barcode: str,
    exclude_product_id: int | None = None,
    exclude_presentation_id: int | None = None,
) -> bool:
    """Tell whether a product OR a presentation already uses this barcode.

    Both are checked together: a scanned code must point to exactly one thing.
    """
    product_query = select(Product.id).where(Product.barcode == barcode)
    if exclude_product_id is not None:
        product_query = product_query.where(Product.id != exclude_product_id)
    presentation_query = select(Presentation.id).where(Presentation.barcode == barcode)
    if exclude_presentation_id is not None:
        presentation_query = presentation_query.where(Presentation.id != exclude_presentation_id)
    return (
        session.scalar(product_query.limit(1)) is not None
        or session.scalar(presentation_query.limit(1)) is not None
    )


def _with_presentations():
    """Load presentations and their prices in two extra queries (not one per product)."""
    return selectinload(Product.presentations).selectinload(Presentation.price_tiers)


def get_product(session: Session, product_id: int) -> Product | None:
    """A product with its presentations and prices."""
    return session.scalar(
        select(Product).where(Product.id == product_id).options(_with_presentations())
    )


def search_products(
    session: Session,
    text: str | None,
    category_id: int | None,
    only_active: bool,
    limit: int,
    offset: int,
) -> tuple[list[Product], int]:
    """Products whose name contains the text, or whose SKU or barcode equals it."""
    conditions = []
    if text:
        lowered = text.strip().lower()
        pattern = f"%{lowered.replace('%', r'\%').replace('_', r'\_')}%"
        conditions.append(
            or_(
                func.lower(Product.name).like(pattern, escape="\\"),
                func.lower(Product.sku) == lowered,
                Product.barcode == text.strip(),
            )
        )
    if category_id is not None:
        conditions.append(Product.category_id == category_id)
    if only_active:
        conditions.append(Product.active.is_(True))

    total = session.scalar(select(func.count(Product.id)).where(*conditions))
    page = session.scalars(
        select(Product)
        .where(*conditions)
        .options(_with_presentations())
        .order_by(func.lower(Product.name), Product.id)
        .limit(limit)
        .offset(offset)
    )
    return list(page), total or 0


def get_presentation(session: Session, presentation_id: int) -> Presentation | None:
    """A presentation with its prices and its product."""
    return session.scalar(
        select(Presentation)
        .where(Presentation.id == presentation_id)
        .options(selectinload(Presentation.price_tiers), selectinload(Presentation.product))
    )


def presentation_name_taken(
    session: Session, product_id: int, name: str, exclude_id: int | None = None
) -> bool:
    """Tell whether the product already has a presentation with this name."""
    query = select(Presentation.id).where(
        Presentation.product_id == product_id, Presentation.name == name
    )
    if exclude_id is not None:
        query = query.where(Presentation.id != exclude_id)
    return session.scalar(query.limit(1)) is not None


def get_minimum_stock(session: Session, product_id: int, location_id: int) -> MinimumStock | None:
    """The alert threshold of a product in a location, if any."""
    return session.get(MinimumStock, (product_id, location_id))
