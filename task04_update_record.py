"""Задание 4 (средняя сложность): обновить запись.

sqlite3: таблица students, параметризованный UPDATE с проверкой
rowcount, коммит через контекстный менеджер соединения (rollback
при ошибке - автоматически). Все функции принимают соединение
параметром, поэтому тесты работают на in-memory базе.

Запуск: python task04_update_record.py
"""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    grade INTEGER NOT NULL CHECK (grade BETWEEN 2 AND 5)
)
"""

SEED = [
    ("Полошков Ярослав Витальевич", "220042-11", 4),
    ("Иванов Иван Иванович", "220042-11", 3),
    ("Петрова Анна Сергеевна", "221341", 5),
]


def init_db(connection: sqlite3.Connection) -> None:
    """Создаёт таблицу и наполняет её начальными данными."""
    with connection:
        connection.execute(SCHEMA)
        connection.executemany(
            "INSERT INTO students (full_name, group_name, grade) "
            "VALUES (?, ?, ?)", SEED)


def get_student(connection: sqlite3.Connection,
                student_id: int) -> tuple | None:
    """Возвращает запись студента по id или None."""
    cursor = connection.execute(
        "SELECT id, full_name, group_name, grade FROM students "
        "WHERE id = ?", (student_id,))
    return cursor.fetchone()


def update_grade(connection: sqlite3.Connection, student_id: int,
                 grade: int) -> int:
    """Обновляет оценку; возвращает число изменённых строк (0/1).

    Параметры подставляются через плейсхолдеры - SQL-инъекция
    исключена. Отсутствующий id даёт rowcount = 0.
    """
    if not 2 <= grade <= 5:
        raise ValueError(f"оценка должна быть от 2 до 5, "
                         f"получено {grade}")
    with connection:
        cursor = connection.execute(
            "UPDATE students SET grade = ? WHERE id = ?",
            (grade, student_id))
    return cursor.rowcount


def demo() -> None:
    """Демонстрация UPDATE на in-memory базе."""
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    print("До UPDATE:   ", get_student(connection, 1))
    changed = update_grade(connection, 1, 5)
    print(f"UPDATE students SET grade = 5 WHERE id = 1; "
          f"изменено строк: {changed}")
    print("После UPDATE:", get_student(connection, 1))
    print("UPDATE несуществующего id=999:",
          update_grade(connection, 999, 4), "строк изменено")
    print("Попытка поставить оценку 10:")
    try:
        update_grade(connection, 1, 10)
    except ValueError as error:
        print(f"  Ошибка: {error}")
    connection.close()


if __name__ == "__main__":
    demo()
