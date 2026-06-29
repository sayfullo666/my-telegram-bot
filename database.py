import asyncpg
import os

DB_URL = os.environ.get("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id SERIAL PRIMARY KEY,
            channel_id TEXT NOT NULL,
            channel_name TEXT NOT NULL,
            channel_link TEXT NOT NULL
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            year TEXT,
            genre TEXT,
            message_id INTEGER NOT NULL
        )
    """)
    await conn.close()

async def get_channels():
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("SELECT * FROM channels")
    await conn.close()
    return rows

async def add_channel(channel_id: str, channel_name: str, channel_link: str):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute(
        "INSERT INTO channels (channel_id, channel_name, channel_link) VALUES ($1, $2, $3)",
        channel_id, channel_name, channel_link
    )
    await conn.close()

async def remove_channel(channel_id: str):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("DELETE FROM channels WHERE channel_id = $1", channel_id)
    await conn.close()

async def get_movie(code: str):
    conn = await asyncpg.connect(DB_URL)
    row = await conn.fetchrow("SELECT * FROM movies WHERE code = $1", code)
    await conn.close()
    return row

async def add_movie(code, title, description, year, genre, message_id):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute(
        "INSERT INTO movies (code, title, description, year, genre, message_id) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (code) DO UPDATE SET title=$2, description=$3, year=$4, genre=$5, message_id=$6",
        code, title, description, year, genre, message_id
    )
    await conn.close()

async def delete_movie(code: str):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("DELETE FROM movies WHERE code = $1", code)
    await conn.close()

async def get_all_movies():
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("SELECT * FROM movies ORDER BY id DESC")
    await conn.close()
    return rows
