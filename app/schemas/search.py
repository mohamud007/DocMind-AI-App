from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural language search query"
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Maximum number of search results"
    )