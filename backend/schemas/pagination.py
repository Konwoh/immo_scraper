from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from fastapi import Depends
from typing import Annotated

MAX_RESULTS_PER_PAGE = 50
T = TypeVar("T")


class PaginationInput(BaseModel):
    """Model passed in the request to validate pagination input."""

    page: int = Field(default=1, ge=1, description="Requested page number")
    page_size: int = Field(
        default=25,
        ge=1,
        le=MAX_RESULTS_PER_PAGE,
        description="Requested number of items per page",
    )


class Page(BaseModel, Generic[T]):
    """Model to represent a page of results along with pagination metadata."""

    items: list[T] = Field(description="List of items on this Page")
    total_items: int = Field(ge=0, description="Number of total items")
    start_index: int = Field(ge=0, description="Starting item index")
    end_index: int = Field(ge=0, description="Ending item index")
    total_pages: int = Field(ge=0, description="Total number of pages")
    current_page: int = Field(ge=0, description="Page number (could differ from request)")
    current_page_size: int = Field(
        ge=0, description="Number of items per page (could differ from request)"
    )
    
PaginationDep = Annotated[PaginationInput, Depends()]

def paginate(query, pagination_input: PaginationInput):
    total_items = query.count()

    total_pages = (total_items + pagination_input.page_size - 1) // pagination_input.page_size
    total_pages = max(total_pages, 1)

    current_page = min(pagination_input.page, total_pages)
    offset = (current_page - 1) * pagination_input.page_size

    items = query.offset(offset).limit(pagination_input.page_size).all()

    return Page(
        items=items,
        total_items=total_items,
        start_index=offset + 1 if total_items > 0 else 0,
        end_index=min(offset + pagination_input.page_size, total_items),
        total_pages=total_pages,
        current_page=current_page,
        current_page_size=len(items),
    )
