# quick_fix.py — run once, then delete
import asyncio
from sqlalchemy import text
from database import engine

async def fix():
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE users SET is_admin = false WHERE is_admin IS NULL"))

asyncio.run(fix())