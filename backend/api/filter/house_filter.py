from enum import Enum

from pydantic import BaseModel, Field, model_validator

from backend.database.models import House

_EINFAMILIENHAUS_VARIANTS = ["Einfamilienhaus freistehend", "Einfamilienhaus (freistehend)"]


class HouseEstateType(str, Enum):
    einfamilienhaus = "Einfamilienhaus freistehend"
    doppelhaushaelfte = "Doppelhaushälfte"
    reihenhaus = "Reihenhaus"
    reihenmittelhaus = "Reihenmittelhaus"
    reiheneckhaus = "Reiheneckhaus"
    mehrfamilienhaus = "Mehrfamilienhaus"
    bungalow = "Bungalow"
    villa = "Villa"
    bauernhaus = "Bauernhaus"
    wohnimmobilie_sonstige = "Wohnimmobilie (sonstige)"
    andere_haustypen = "Andere Haustypen"


class HouseFilter(BaseModel):
    city: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    min_living_space: float | None = Field(default=None, ge=0)
    max_living_space: float | None = Field(default=None, ge=0)
    min_rooms: float | None = Field(default=None, ge=0)
    max_rooms: float | None = Field(default=None, ge=0)
    estate_type: HouseEstateType | None = None

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


def apply_house_filter(query, f: HouseFilter):
    if f.city:
        query = query.filter(House.city.ilike(f"%{f.city}%"))
    if f.min_price is not None:
        query = query.filter(House.price >= f.min_price)
    if f.max_price is not None:
        query = query.filter(House.price <= f.max_price)
    if f.min_living_space is not None:
        query = query.filter(House.living_space >= f.min_living_space)
    if f.max_living_space is not None:
        query = query.filter(House.living_space <= f.max_living_space)
    if f.min_rooms is not None:
        query = query.filter(House.rooms >= f.min_rooms)
    if f.max_rooms is not None:
        query = query.filter(House.rooms <= f.max_rooms)
    if f.estate_type is HouseEstateType.einfamilienhaus:
        # DB kennt zwei Schreibweisen fuer denselben Typ
        query = query.filter(House.estate_type.in_(_EINFAMILIENHAUS_VARIANTS))
    elif f.estate_type is not None:
        query = query.filter(House.estate_type == f.estate_type.value)
    return query
