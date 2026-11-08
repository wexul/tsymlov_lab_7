"""Модульные тесты задания 4 (повышенная): индексация и поиск.

Остальные задания покрыты набором advanced10_db_tests.py (это и есть
задание 10 повышенной сложности). Запуск всех тестов разом:
python -m unittest -v
"""

from __future__ import annotations

import sqlite3
import unittest

from advanced04_index_search import (
    SEARCH_PREFIX,
    create_name_index,
    explain_search,
    init_db,
    measure_search,
    search_by_prefix,
)


class TestIndexSearch(unittest.TestCase):
    """Индексация и поиск по префиксу."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        init_db(self.connection, rows=200)

    def tearDown(self) -> None:
        self.connection.close()

    def test_prefix_search_results(self) -> None:
        rows = search_by_prefix(self.connection, SEARCH_PREFIX)
        self.assertTrue(rows)
        for row in rows:
            self.assertTrue(row[1].startswith(SEARCH_PREFIX))

    def test_no_matches(self) -> None:
        self.assertEqual(search_by_prefix(self.connection, "Zzz"), [])

    def test_plan_scan_without_index(self) -> None:
        plan = " ".join(explain_search(self.connection, SEARCH_PREFIX))
        self.assertIn("SCAN", plan)
        self.assertNotIn("SEARCH", plan)

    def test_plan_search_with_index(self) -> None:
        create_name_index(self.connection)
        plan = " ".join(explain_search(self.connection, SEARCH_PREFIX))
        self.assertIn("SEARCH", plan)
        self.assertIn("idx_students_name", plan)

    def test_results_identical_with_index(self) -> None:
        before = search_by_prefix(self.connection, SEARCH_PREFIX)
        create_name_index(self.connection)
        after = search_by_prefix(self.connection, SEARCH_PREFIX)
        self.assertEqual(before, after)

    def test_measure_search_returns_positive(self) -> None:
        elapsed = measure_search(self.connection, SEARCH_PREFIX,
                                 repeats=3)
        self.assertGreater(elapsed, 0)


if __name__ == "__main__":
    unittest.main()
