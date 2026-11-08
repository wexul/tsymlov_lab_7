"""Задание 10 (повышенная сложность): unit-тесты базы данных.

Набор unittest для всех модулей работы с БД: sqlite3 (обновление
записи, JOIN) и SQLAlchemy ORM (одна таблица). Каждый тест получает
свежую in-memory базу в setUp - тесты изолированы и не зависят от
порядка выполнения.

Запуск: python -m unittest advanced10_db_tests -v
"""

from __future__ import annotations

import sqlite3
import unittest

from task04_update_record import (
    get_student,
    init_db as init_update_db,
    update_grade,
)
from task08_join import (
    group_statistics,
    init_db as init_join_db,
    students_with_groups,
)
from task10_sqlalchemy_table import (
    add_book,
    delete_book,
    get_books,
    init_db as init_orm_db,
    make_engine,
    update_year,
)


class TestUpdateRecord(unittest.TestCase):
    """Обновление записи в sqlite3."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        init_update_db(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_update_existing(self) -> None:
        self.assertEqual(update_grade(self.connection, 1, 5), 1)
        self.assertEqual(get_student(self.connection, 1)[3], 5)

    def test_update_missing_returns_zero(self) -> None:
        self.assertEqual(update_grade(self.connection, 999, 4), 0)

    def test_update_validation(self) -> None:
        with self.assertRaises(ValueError):
            update_grade(self.connection, 1, 6)
        self.assertEqual(get_student(self.connection, 1)[3], 4)

    def test_get_missing_student(self) -> None:
        self.assertIsNone(get_student(self.connection, 42))

    def test_update_is_persistent(self) -> None:
        update_grade(self.connection, 2, 5)
        fresh = self.connection.execute(
            "SELECT grade FROM students WHERE id = 2").fetchone()
        self.assertEqual(fresh[0], 5)


class TestJoin(unittest.TestCase):
    """JOIN двух связанных таблиц."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        init_join_db(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_inner_join_rows(self) -> None:
        rows = students_with_groups(self.connection)
        self.assertEqual(len(rows), 3)
        names = {row[0] for row in rows}
        self.assertIn("Полошков Ярослав Витальевич", names)
        for row in rows:
            self.assertEqual(len(row), 4)

    def test_left_join_includes_empty_group(self) -> None:
        stats = {row[0]: row for row in group_statistics(self.connection)}
        self.assertEqual(stats["229999"][1], 0)
        self.assertIsNone(stats["229999"][2])
        self.assertEqual(stats["220042-11"][1], 2)
        self.assertAlmostEqual(stats["220042-11"][2], 4.5)

    def test_foreign_key_link(self) -> None:
        orphan = self.connection.execute(
            "SELECT COUNT(*) FROM students AS s "
            "LEFT JOIN groups AS g ON g.id = s.group_id "
            "WHERE g.id IS NULL").fetchone()
        self.assertEqual(orphan[0], 0)


class TestOrmSingleTable(unittest.TestCase):
    """SQLAlchemy ORM для одной таблицы books."""

    def setUp(self) -> None:
        self.engine = make_engine("sqlite:///:memory:")
        init_orm_db(self.engine)

    def test_add_and_get(self) -> None:
        book = add_book(self.engine, "Чистый код", "Роберт Мартин", 2008)
        self.assertEqual(book.id, 1)
        self.assertEqual(len(get_books(self.engine)), 1)

    def test_filter_by_author(self) -> None:
        add_book(self.engine, "A", "Автор1", 2000)
        add_book(self.engine, "B", "Автор2", 2001)
        filtered = get_books(self.engine, author="Автор2")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "B")

    def test_update_year(self) -> None:
        book = add_book(self.engine, "A", "Автор", 2000)
        self.assertEqual(update_year(self.engine, book.id, 2020).year,
                         2020)
        with self.assertRaises(LookupError):
            update_year(self.engine, 999, 2000)

    def test_delete(self) -> None:
        book = add_book(self.engine, "A", "Автор", 2000)
        delete_book(self.engine, book.id)
        self.assertEqual(get_books(self.engine), [])
        with self.assertRaises(LookupError):
            delete_book(self.engine, book.id)

    def test_validation(self) -> None:
        for args in [("", "Автор", 2000), ("A", "", 2000),
                     ("A", "Автор", -5)]:
            with self.assertRaises(ValueError):
                add_book(self.engine, *args)


if __name__ == "__main__":
    unittest.main()
