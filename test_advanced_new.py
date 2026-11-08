"""Тесты транзакций, асинхронного CRUD и защиты от SQL-инъекций."""

from __future__ import annotations

import asyncio
import sqlite3
import unittest

import aiosqlite

from advanced05_transactions import (
    TransferError,
    get_balances,
    init_db as init_accounts,
    transfer,
)
from advanced09_async_db import (
    add_note,
    delete_note,
    get_notes,
    init_db as init_notes,
    update_note,
)
from task06_parameterized_queries import (
    PAYLOAD,
    find_user_safe,
    find_user_unsafe,
    init_db as init_users,
)


class TestTransactions(unittest.TestCase):
    """Повышенная №5: commit и rollback."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        init_accounts(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_successful_commit(self) -> None:
        transfer(self.connection, 1, 2, 30)
        balances = get_balances(self.connection)
        self.assertEqual(balances[0][2], 70)
        self.assertEqual(balances[1][2], 130)

    def test_rollback_on_constraint_violation(self) -> None:
        before = get_balances(self.connection)
        with self.assertRaises(sqlite3.IntegrityError):
            transfer(self.connection, 1, 2, 500)
        self.assertEqual(get_balances(self.connection), before)

    def test_rollback_on_missing_account(self) -> None:
        before = get_balances(self.connection)
        with self.assertRaises(TransferError):
            transfer(self.connection, 1, 999, 10)
        self.assertEqual(get_balances(self.connection), before)

    def test_invalid_amount(self) -> None:
        with self.assertRaises(ValueError):
            transfer(self.connection, 1, 2, 0)


class TestAsyncDb(unittest.TestCase):
    """Повышенная №9: асинхронный CRUD через aiosqlite."""

    def test_crud(self) -> None:
        async def scenario() -> None:
            async with aiosqlite.connect(":memory:") as db:
                await init_notes(db)
                first = await add_note(db, "A", "текст")
                await add_note(db, "B")
                self.assertEqual(len(await get_notes(db)), 2)
                self.assertEqual(await update_note(db, first, "новый"),
                                 1)
                self.assertEqual(await update_note(db, 999, "x"), 0)
                self.assertEqual(await delete_note(db, first), 1)
                self.assertEqual(len(await get_notes(db)), 1)
                with self.assertRaises(ValueError):
                    await add_note(db, "  ")
        asyncio.run(scenario())


class TestSqlInjection(unittest.TestCase):
    """Средняя №6: параметризованные запросы."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        init_users(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_unsafe_leaks_table(self) -> None:
        self.assertEqual(len(find_user_unsafe(self.connection,
                                              PAYLOAD)), 2)

    def test_safe_blocks_injection(self) -> None:
        self.assertEqual(find_user_safe(self.connection, PAYLOAD), [])
        self.assertEqual(len(find_user_safe(self.connection,
                                            "Ярослав")), 1)


if __name__ == "__main__":
    unittest.main()
