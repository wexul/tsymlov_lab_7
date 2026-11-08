"""Задание 6 (средняя сложность): использовать параметры запроса.

Явная демонстрация защиты от SQL-инъекций: один и тот же поиск по
имени выполнен дважды - уязвимой конкатенацией строк и безопасным
параметризованным запросом. Полезная нагрузка ' OR '1'='1 ломает
первый вариант (возвращает всю таблицу) и бессильна против второго.

Запуск: python task06_parameterized_queries.py
"""

from __future__ import annotations

import sqlite3

PAYLOAD = "' OR '1'='1"


def init_db(connection: sqlite3.Connection) -> None:
    """Создаёт таблицу пользователей с парой записей."""
    with connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
            "secret TEXT NOT NULL)")
        connection.executemany(
            "INSERT INTO users (name, secret) VALUES (?, ?)",
            [("Ярослав", "секрет-1"), ("Иван", "секрет-2")])


def find_user_unsafe(connection: sqlite3.Connection,
                     name: str) -> list[tuple]:
    """УЯЗЫВИМЫЙ вариант: конкатенация ввода в SQL. Только для демо!"""
    query = ("SELECT id, name, secret FROM users WHERE name = '"
             + name + "'")
    return connection.execute(query).fetchall()


def find_user_safe(connection: sqlite3.Connection,
                   name: str) -> list[tuple]:
    """Безопасный вариант: параметр через плейсхолдер."""
    return connection.execute(
        "SELECT id, name, secret FROM users WHERE name = ?",
        (name,)).fetchall()


def demo() -> None:
    """Показывает разницу между конкатенацией и параметрами."""
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    print("Обычный ввод 'Ярослав':")
    print("  unsafe:", find_user_unsafe(connection, "Ярослав"))
    print("  safe:  ", find_user_safe(connection, "Ярослав"))
    print(f"Полезная нагрузка: {PAYLOAD}")
    unsafe = find_user_unsafe(connection, PAYLOAD)
    print(f"  unsafe: утечка {len(unsafe)} записей - ВСЯ таблица: "
          f"{unsafe}")
    safe = find_user_safe(connection, PAYLOAD)
    print(f"  safe:   {len(safe)} записей - инъекция не сработала, "
          "строка искалась как обычное имя")
    connection.close()


if __name__ == "__main__":
    demo()
