"""HTTP endpoints of the catalog (docs/09). Each one declares the permission it needs."""

from typing import Annotated, Any

from almacen_security import TokenClaims
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from core.catalog import repository as repo
from core.catalog import service
from core.catalog.models import Brand, Category, Location, Product
from core.catalog.schemas import (
    LocationCreate,
    LocationOut,
    LocationUpdate,
    MinimumStockIn,
    NamedCreate,
    NamedOut,
    NamedUpdate,
    PresentationCreate,
    PresentationUpdate,
    PriceTiersReplace,
    ProductCreate,
    ProductOut,
    ProductPage,
    ProductUpdate,
)
from core.db import get_session
from core.errors import NotFoundError
from core.security import guard

router = APIRouter(prefix="/v1", tags=["catalog"])

DbSession = Annotated[Session, Depends(get_session)]
LoggedIn = Annotated[TokenClaims, Depends(guard.current_user())]
CatalogManager = Annotated[TokenClaims, Depends(guard.require("catalog.manage"))]
PriceEditor = Annotated[TokenClaims, Depends(guard.require("price.edit"))]
LocationManager = Annotated[TokenClaims, Depends(guard.require("location.manage"))]
StockReader = Annotated[TokenClaims, Depends(guard.require("stock.read"))]

_ERRORS = {
    401: {"description": "Missing or invalid token"},
    403: {"description": "Missing permission"},
}
_PRODUCT = {200: {"model": ProductOut}, **_ERRORS}


def product_out(product: Product, user: TokenClaims) -> dict[str, Any]:
    """A product as JSON; the cost is left out unless the user has cost.view (RNF-14)."""
    data = ProductOut.model_validate(product).model_dump(mode="json")
    if not user.has("cost.view"):
        data.pop("cost")
    return data


def _require_cost_permission(user: TokenClaims, sends_cost: bool) -> None:
    """Sending a cost needs cost.view, even with catalog.manage (docs/06 D2)."""
    if sends_cost and not user.has("cost.view"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Missing permission")


# ---------- categories and brands (support lists: any logged-in user can read them) ----------


@router.get("/categories", responses=_ERRORS)
def list_categories(_: LoggedIn, session: DbSession, all: bool = False) -> list[NamedOut]:
    """Product categories, sorted by name. Only active ones unless all=true."""
    return repo.list_all(session, Category, only_active=not all)


@router.post("/categories", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
def create_category(body: NamedCreate, user: CatalogManager, session: DbSession) -> NamedOut:
    """Create a category (the name cannot repeat, regardless of case)."""
    return service.create_named(session, user, "category", body)


@router.patch("/categories/{category_id}", responses=_ERRORS)
def update_category(
    category_id: int, body: NamedUpdate, user: CatalogManager, session: DbSession
) -> NamedOut:
    """Rename or (de)activate a category."""
    return service.update_named(session, user, "category", category_id, body)


@router.get("/brands", responses=_ERRORS)
def list_brands(_: LoggedIn, session: DbSession, all: bool = False) -> list[NamedOut]:
    """Brands, sorted by name. Only active ones unless all=true."""
    return repo.list_all(session, Brand, only_active=not all)


@router.post("/brands", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
def create_brand(body: NamedCreate, user: CatalogManager, session: DbSession) -> NamedOut:
    """Create a brand (the name cannot repeat, regardless of case)."""
    return service.create_named(session, user, "brand", body)


@router.patch("/brands/{brand_id}", responses=_ERRORS)
def update_brand(
    brand_id: int, body: NamedUpdate, user: CatalogManager, session: DbSession
) -> NamedOut:
    """Rename or (de)activate a brand."""
    return service.update_named(session, user, "brand", brand_id, body)


# ---------- locations ----------


@router.get("/locations", responses=_ERRORS)
def list_locations(_: LoggedIn, session: DbSession, all: bool = False) -> list[LocationOut]:
    """Stores and warehouses, sorted by name. Only active ones unless all=true."""
    return repo.list_all(session, Location, only_active=not all)


@router.post("/locations", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
def create_location(body: LocationCreate, user: LocationManager, session: DbSession) -> LocationOut:
    """Create a store (STORE) or warehouse (WAREHOUSE)."""
    return service.create_location(session, user, body)


@router.patch("/locations/{location_id}", responses=_ERRORS)
def update_location(
    location_id: int, body: LocationUpdate, user: LocationManager, session: DbSession
) -> LocationOut:
    """Rename, change the address or (de)activate a location."""
    return service.update_location(session, user, location_id, body)


# ---------- products ----------


@router.get("/products", responses={200: {"model": ProductPage}, **_ERRORS})
def search_products(
    user: StockReader,
    session: DbSession,
    q: Annotated[str | None, Query(max_length=100, description="Name, SKU or barcode")] = None,
    category_id: int | None = None,
    all: bool = False,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    """Search products by name (contains), SKU or barcode (exact). Paginated."""
    products, total = repo.search_products(session, q, category_id, not all, limit, offset)
    return {"items": [product_out(p, user) for p in products], "total": total}


@router.get("/products/{product_id}", responses={**_PRODUCT, 404: {"description": "Not found"}})
def get_product(product_id: int, user: StockReader, session: DbSession) -> dict[str, Any]:
    """A product with its presentations and price tiers."""
    product = repo.get_product(session, product_id)
    if product is None:
        raise NotFoundError("The product does not exist")
    return product_out(product, user)


@router.post("/products", status_code=status.HTTP_201_CREATED, responses=_PRODUCT)
def create_product(body: ProductCreate, user: CatalogManager, session: DbSession) -> dict[str, Any]:
    """Create a product; its base presentation (factor 1) is created with it.

    Sending a cost also needs cost.view.
    """
    _require_cost_permission(user, body.cost is not None)
    return product_out(service.create_product(session, user, body), user)


@router.patch("/products/{product_id}", responses=_PRODUCT)
def update_product(
    product_id: int, body: ProductUpdate, user: CatalogManager, session: DbSession
) -> dict[str, Any]:
    """Change a product. SKU and base unit cannot change. Changing the cost needs cost.view."""
    _require_cost_permission(user, "cost" in body.model_fields_set)
    return product_out(service.update_product(session, user, product_id, body), user)


@router.post(
    "/products/{product_id}/presentations",
    status_code=status.HTTP_201_CREATED,
    responses=_PRODUCT,
)
def add_presentation(
    product_id: int, body: PresentationCreate, user: CatalogManager, session: DbSession
) -> dict[str, Any]:
    """Add a presentation (CAJA, DOCENA...) with its factor, which cannot change later."""
    return product_out(service.add_presentation(session, user, product_id, body), user)


@router.patch("/presentations/{presentation_id}", responses=_PRODUCT)
def update_presentation(
    presentation_id: int, body: PresentationUpdate, user: CatalogManager, session: DbSession
) -> dict[str, Any]:
    """Rename, change the barcode or (de)activate a presentation (never its factor)."""
    return product_out(service.update_presentation(session, user, presentation_id, body), user)


@router.put("/presentations/{presentation_id}/price-tiers", responses=_PRODUCT)
def replace_price_tiers(
    presentation_id: int, body: PriceTiersReplace, user: PriceEditor, session: DbSession
) -> dict[str, Any]:
    """Replace all the price tiers of a presentation (there must be one from quantity 1)."""
    return product_out(
        service.replace_price_tiers(session, user, presentation_id, body.tiers), user
    )


@router.put(
    "/products/{product_id}/minimum-stock/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_ERRORS,
)
def set_minimum_stock(
    product_id: int,
    location_id: int,
    body: MinimumStockIn,
    user: CatalogManager,
    session: DbSession,
) -> Response:
    """Set the alert threshold of a product in a location, in base units (0 = no alert)."""
    service.set_minimum_stock(session, user, product_id, location_id, body.quantity)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
