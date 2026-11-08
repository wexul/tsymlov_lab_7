"""Задание 4 (повышенная сложность): индексация и поиск.

sqlite3: таблица students на 5000 записей (генерируются
детерминированно). Поиск по префиксу фамилии (диапазонный запрос
full_name >= prefix AND full_name < next) выполняется до и после
CREATE INDEX; план через EXPLAIN QUERY PLAN показывает переход
от SCAN к SEARCH с использованием индекса, время замеряется
perf_counter.

Запуск: python advanced04_index_search.py
"""

from __future__ import annotations

import sqlite3
import time

ROW_COUNT = 5000
SEARCH_PREFIX = "Петров"


def init_db(connection: sqlite3.Connection,
            rows: int = ROW_COUNT) -> None:
    """Создаёт таблицу и rows детерминированных записей."""
    with connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS students ("
            "id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, "
            "group_name TEXT NOT NULL, grade INTEGER NOT NULL)")
        data = [
            (f"{surname}{suffix} Студент{index:04d}",
             f"2200{index % 50:02d}", 2 + index % 4)
            for index, (surname, suffix) in enumerate(
                (("Иванов", "а") if i % 2 == 0 else ("Петров", "")
                 for i in range(rows)))
        ]
        connection.executemany(
            "INSERT INTO students (full_name, group_name, grade) "
            "VALUES (?, ?, ?)", data)


def create_name_index(connection: sqlite3.Connection) -> None:
    """Создаёт индекс по полю full_name."""
    with connection:
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_students_name "
            "ON students(full_name)")


def search_by_prefix(connection: sqlite3.Connection,
                     prefix: str) -> list[tuple]:
    """Ищет студентов по префиксу ФИО.

    Вместо LIKE 'prefix%' используется эквивалентный диапазон
    full_name >= prefix AND full_name < prefix + U+10FFFF: SQLite
    не применяет индекс к LIKE с bound-параметром, а диапазонный
    запрос выполняется как SEARCH по индексу. Параметры подставляются
    плейсхолдерами, SQL-инъекция исключена.
    """
    cursor = connection.execute(
        "SELECT id, full_name, group_name, grade FROM students "
        "WHERE full_name >= ? AND full_name < ? "
        "ORDER BY full_name LIMIT 5",
        (prefix, prefix + "\U0010ffff"))
    return cursor.fetchall()


def explain_search(connection: sqlite3.Connection,
                   prefix: str) -> list[str]:
    """Возвращает план запроса EXPLAIN QUERY PLAN."""
    cursor = connection.execute(
        "EXPLAIN QUERY PLAN SELECT id FROM students "
        "WHERE full_name >= ? AND full_name < ?",
        (prefix, prefix + "\U0010ffff"))
    return [row[-1] for row in cursor.fetchall()]


def measure_search(connection: sqlite3.Connection, prefix: str,
                   repeats: int = 50) -> float:
    """Среднее время одного поиска, миллисекунды."""
    start = time.perf_counter()
    for _ in range(repeats):
        search_by_prefix(connection, prefix)
    return (time.perf_counter() - start) / repeats * 1000


def demo() -> None:
    """Сравнение поиска без индекса и с индексом."""
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    print(f"Таблица students: {ROW_COUNT} записей")
    before_plan = explain_search(connection, SEARCH_PREFIX)
    before_time = measure_search(connection, SEARCH_PREFIX)
    print(f"Без индекса: план {before_plan}, "
          f"{before_time:.3f} мс/запрос")
    create_name_index(connection)
    after_plan = explain_search(connection, SEARCH_PREFIX)
    after_time = measure_search(connection, SEARCH_PREFIX)
    print(f"С индексом:  план {after_plan}, "
          f"{after_time:.3f} мс/запрос")
    print(f"Пример поиска '{SEARCH_PREFIX}%' (первые 5):")
    for row in search_by_prefix(connection, SEARCH_PREFIX):
        print("  ", row)
    connection.close()


if __name__ == "__main__":
    demo()
