from pydantic import BaseModel
from typing import List


class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int

    class Config:
        orm_mode = True


class ItemListResponse(BaseModel):
    total: int
    items: List[ItemRead]
