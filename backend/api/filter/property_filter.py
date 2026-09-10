from enum import Enum

from pydantic import BaseModel, Field, model_validator

from backend.database.models import Property


class PropertyDevelopment(str, Enum):
    erschlossen = "Erschlossen"
    teilerschlossen = "Teilerschlossen"
    unerschlossen = "Unerschlossen"


class PropertyFilter(BaseModel):
    city: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    min_space: float | None = Field(default=None, ge=0)
    max_space: float | None = Field(default=None, ge=0)
    development: PropertyDevelopment | None = None

    @model_validator(mode="after")
    def _ranges_consistent(self):
        for lo, hi in (("min_price", "max_price"), ("min_space", "max_space")):
            a, b = getattr(self, lo), getattr(self, hi)
            if a is not None and b is not None and a > b:
                raise ValueError(f"{lo} darf nicht groesser als {hi} sein")
        return self


def apply_property_filter(query, f: PropertyFilter):
    if f.city:
        query = query.filter(Property.city.ilike(f"%{f.city}%"))
    if f.min_price is not None:
        query = query.filter(Property.price >= f.min_price)
    if f.max_price is not None:
        query = query.filter(Property.price <= f.max_price)
    if f.min_space is not None:
        query = query.filter(Property.space >= f.min_space)
    if f.max_space is not None:
        query = query.filter(Property.space <= f.max_space)
    if f.development is not None:
        query = query.filter(Property.development == f.development.value)
    return query
