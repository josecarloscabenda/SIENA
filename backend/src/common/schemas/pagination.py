from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list
