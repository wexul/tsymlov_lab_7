"""Задание 8 (средняя сложность): выполнить JOIN.

sqlite3, две связанные таблицы: groups (группы) и students
(студенты, внешний ключ group_id). INNER JOIN выводит студентов
вместе с названием группы, LEFT JOIN + GROUP BY - число студентов
в каждой группе, включая группу без студентов.

Запуск: python task08_join.py
"""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    faculty TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    group_id INTEGER NOT NULL REFERENCES groups(id),
    grade INTEGER NOT NULL
);
"""

GROUPS = [("220042-11", "Информатика"), ("221341", "Математика"),
          ("229999", "Физика")]
STUDENTS = [
    ("Полошков Ярослав Витальевич", 1, 5),
    ("Иванов Иван Иванович", 1, 4),
    ("Петрова Анна Сергеевна", 2, 5),
]


def init_db(connection: sqlite3.Connection) -> None:
    """Создаёт обе таблицы и начальные данные."""
    with connection:
        connection.executescript(SCHEMA)
        connection.executemany(
            "INSERT INTO groups (name, faculty) VALUES (?, ?)", GROUPS)
        connection.executemany(
            "INSERT INTO students (full_name, group_id, grade) "
            "VALUES (?, ?, ?)", STUDENTS)


def students_with_groups(connection: sqlite3.Connection) -> list[tuple]:
    """INNER JOIN: студент + название группы + факультет."""
    cursor = connection.execute(
        "SELECT s.full_name, g.name, g.faculty, s.grade "
        "FROM students AS s "
        "INNER JOIN groups AS g ON g.id = s.group_id "
        "ORDER BY s.full_name")
    return cursor.fetchall()


def group_statistics(connection: sqlite3.Connection) -> list[tuple]:
    """LEFT JOIN + GROUP BY: число студентов и средний балл группы."""
    cursor = connection.execute(
        "SELECT g.name, COUNT(s.id) AS total, "
        "ROUND(AVG(s.grade), 2) AS avg_grade "
        "FROM groups AS g "
        "LEFT JOIN students AS s ON s.group_id = g.id "
        "GROUP BY g.id, g.name ORDER BY g.name")
    return cursor.fetchall()


def demo() -> None:
    """Демонстрация JOIN-запросов."""
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    print("INNER JOIN (студенты и их группы):")
    for row in students_with_groups(connection):
        print("  ", row)
    print("LEFT JOIN + GROUP BY (статистика по группам):")
    for row in group_statistics(connection):
        print("  ", row)
    print("Группа 229999 без студентов попала в LEFT JOIN "
          "с total = 0 и avg_grade = NULL.")
    connection.close()


if __name__ == "__main__":
    demo()
