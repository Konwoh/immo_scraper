from enum import Enum

from pydantic import BaseModel, Field, model_validator

from backend.database.models import Apartment


class ApartmentEstateType(str, Enum):
    """Wohnungstypen exakt wie in ``apartments.estate_type`` gespeichert."""

    etagenwohnung = "Etagenwohnung"
    erdgeschosswohnung = "Erdgeschosswohnung"
    dachgeschoss = "Dachgeschoss"
    dachgeschosswohnung = "Dachgeschosswohnung"
    souterrain = "Souterrain"
    hochparterre = "Hochparterre"
    maisonette = "Maisonette"
    terrassenwohnung = "Terrassenwohnung"
    penthouse = "Penthouse"
    loft = "Loft"
    andere_wohnungstypen = "Andere Wohnungstypen"
    sonstige = "Sonstige"


class ApartmentFilter(BaseModel):
    city: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    min_living_space: float | None = Field(default=None, ge=0)
    max_living_space: float | None = Field(default=None, ge=0)
    min_rooms: float | None = Field(default=None, ge=0)
    max_rooms: float | None = Field(default=None, ge=0)
    estate_type: ApartmentEstateType | None = None

    @model_validator(mode="after")
    def _ranges_consistent(self):
        for lo, hi in (
            ("min_price", "max_price"),
            ("min_living_space", "max_living_space"),
            ("min_rooms", "max_rooms"),
        ):
            a, b = getattr(self, lo), getattr(self, hi)
            if a is not None and b is not None and a > b:
                raise ValueError(f"{lo} darf nicht groesser als {hi} sein")
        return self


def apply_apartment_filter(query, f: ApartmentFilter):
    """Wendet die gesetzten Filter auf eine ``Apartment``-Query an (vor ``paginate``)."""

    if f.city:
        query = query.filter(Apartment.city.ilike(f"%{f.city}%"))
    if f.min_price is not None:
        query = query.filter(Apartment.price >= f.min_price)
    if f.max_price is not None:
        query = query.filter(Apartment.price <= f.max_price)
    if f.min_living_space is not None:
        query = query.filter(Apartment.living_space >= f.min_living_space)
    if f.max_living_space is not None:
        query = query.filter(Apartment.living_space <= f.max_living_space)
    if f.min_rooms is not None:
        query = query.filter(Apartment.rooms >= f.min_rooms)
    if f.max_rooms is not None:
        query = query.filter(Apartment.rooms <= f.max_rooms)
    if f.estate_type is not None:
        query = query.filter(Apartment.estate_type == f.estate_type.value)
    return query
