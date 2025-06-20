from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:melek123@localhost:5432/postgres"

app = FastAPI(title="FastAPI Boilerplate", version="1.0")

# SQLAlchemy setup async
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Exemple modèle SQLAlchemy
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Pydantic schema pour validation et serialization
class ItemCreate(BaseModel):
    name: str

class ItemRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Dépendance pour session async
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# Route de base
@app.get("/")
async def root():
    return {"message": "Hello FastAPI Boilerplate with PostgreSQL!"}

# Créer un item
@app.post("/items/", response_model=ItemRead)
async def create_item(item: ItemCreate, session: AsyncSession = Depends(get_session)):
    new_item = Item(name=item.name)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item

# Lister tous les items
@app.get("/items/", response_model=List[ItemRead])
async def read_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item))
    items = result.scalars().all()
    return items

# Initialisation base (à lancer séparément, par exemple dans un script)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
