from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from databases import Database
from .models import Base
from .schemas import ItemCreate, ItemRead, ItemListResponse
from .crud import crud_item
from fastapi import HTTPException

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)
database = Database(DATABASE_URL)

app = FastAPI(title="FastCRUD Demo API")


@app.on_event("startup")
async def on_startup():
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def on_shutdown():
    await database.disconnect()


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.post("/items", response_model=ItemRead)
async def create_item(
    item: ItemCreate,
    session: AsyncSession = Depends(get_session)
):
    return await crud_item.create(session, item)


@app.get("/items/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    item = await crud_item.get(session, id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@app.get("/items", response_model=ItemListResponse)
async def list_items(session: AsyncSession = Depends(get_session)):
    items = await crud_item.get_multi(session)
    return ItemListResponse(total=items['total_count'], items=items['data'])


@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    await crud_item.delete(session, id=item_id)
    return {"deleted": True}
