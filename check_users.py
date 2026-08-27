import asyncio
from sqlalchemy import text
from database import engine

async def check():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, username, is_admin FROM users"))
        for row in result:
            print(row)

asyncio.run(check())