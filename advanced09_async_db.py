"""Задание 9 (повышенная сложность): асинхронный доступ к БД.

aiosqlite: тот же CRUD, что в синхронных заданиях, но через
async def / await. Инициализация, вставка, выборка, обновление и
удаление выполняются асинхронно; демонстрация собирается через
asyncio.gather (конкурентные запросы) и asyncio.run.

Запуск: python advanced09_async_db.py
"""

from __future__ import annotations

import asyncio

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT ''
)
"""


async def init_db(db: aiosqlite.Connection) -> None:
    """Создаёт таблицу заметок."""
    await db.execute(SCHEMA)
    await db.commit()


async def add_note(db: aiosqlite.Connection, title: str,
                   content: str = "") -> int:
    """Асинхронно добавляет заметку, возвращает её id."""
    if not title.strip():
        raise ValueError("заголовок не может быть пустым")
    cursor = await db.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title.strip(), content))
    await db.commit()
    return cursor.lastrowid


async def get_notes(db: aiosqlite.Connection) -> list[tuple]:
    """Асинхронно возвращает все заметки."""
    cursor = await db.execute(
        "SELECT id, title, content FROM notes ORDER BY id")
    return await cursor.fetchall()


async def update_note(db: aiosqlite.Connection, note_id: int,
                      content: str) -> int:
    """Асинхронно обновляет текст; возвращает rowcount (0/1)."""
    cursor = await db.execute(
        "UPDATE notes SET content = ? WHERE id = ?",
        (content, note_id))
    await db.commit()
    return cursor.rowcount


async def delete_note(db: aiosqlite.Connection,
                      note_id: int) -> int:
    """Асинхронно удаляет заметку; возвращает rowcount (0/1)."""
    cursor = await db.execute(
        "DELETE FROM notes WHERE id = ?", (note_id,))
    await db.commit()
    return cursor.rowcount


async def demo() -> None:
    """Асинхронный CRUD с конкурентным запуском операций."""
    async with aiosqlite.connect(":memory:") as db:
        await init_db(db)
        ids = await asyncio.gather(
            add_note(db, "Первая", "async/await"),
            add_note(db, "Вторая", "aiosqlite"),
            add_note(db, "Третья", "asyncio.gather"),
        )
        print("async INSERT (gather):", ids)
        print("async SELECT:", *await get_notes(db), sep="\n  ")
        changed = await update_note(db, ids[0], "обновлено асинхронно")
        print(f"async UPDATE: изменено строк {changed}")
        removed = await delete_note(db, ids[2])
        print(f"async DELETE: удалено строк {removed}")
        print("Осталось заметок:", len(await get_notes(db)))


if __name__ == "__main__":
    asyncio.run(demo())
