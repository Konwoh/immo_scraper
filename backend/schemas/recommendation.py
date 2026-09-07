from pydantic import BaseModel, ConfigDict


class RecommendationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    price: float | None = None
    city: str | None = None
    zip_code: str | None = None
    living_space: float | None = None
    rooms: float | None = None
    estate_type: str | None = None  # granularer DB-Wert, z. B. "Einfamilienhaus"
    images: list[str] = []
    similarity: float


class RecommendationResponse(BaseModel):
    count: int
    items: list[RecommendationItem]
