from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/fastapi_blog"

engine = create_async_engine(DATABASE_URL)

async def test():
    async with engine.begin() as conn:
        print("Connected Successfully!")

asyncio.run(test())