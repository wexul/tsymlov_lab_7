"""Задание 5 (повышенная сложность): транзакции.

sqlite3: явная транзакция с несколькими операциями - перевод баллов
между счетами студентов. Два сценария:
1) успешный перевод -> commit(), обе операции применены;
2) ошибка в середине (нарушение CHECK balance >= 0) -> rollback(),
   ни одна из операций не применилась, балансы прежние.
Транзакция открывается явно (BEGIN IMMEDIATE), а не неявным
with connection:, как в задании 4 средней сложности.

Запуск: python advanced05_transactions.py
"""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    owner TEXT NOT NULL,
    balance INTEGER NOT NULL CHECK (balance >= 0)
)
"""


class TransferError(Exception):
    """Ошибка перевода между счетами."""


def init_db(connection: sqlite3.Connection) -> None:
    """Создаёт таблицу счетов и два счёста по 100 баллов."""
    connection.execute(SCHEMA)
    connection.executemany(
        "INSERT INTO accounts (owner, balance) VALUES (?, ?)",
        [("Ярослав", 100), ("Иван", 100)])
    connection.commit()


def get_balances(connection: sqlite3.Connection) -> list[tuple]:
    """Возвращает все счета (id, owner, balance)."""
    cursor = connection.execute(
        "SELECT id, owner, balance FROM accounts ORDER BY id")
    return cursor.fetchall()


def transfer(connection: sqlite3.Connection, sender_id: int,
             receiver_id: int, amount: int) -> None:
    """Переводит amount баллов между счетами одной транзакцией.

    Обе операции (списание и зачисление) атомарны: при любой ошибке
    выполняется rollback и база остаётся в исходном состоянии.
    """
    if amount <= 0:
        raise ValueError("сумма перевода должна быть положительной")
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, sender_id))
        # Имитация второй операции: если списание ушло в минус,
        # CHECK (balance >= 0) бросит IntegrityError уже здесь.
        connection.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, receiver_id))
        cursor = connection.execute(
            "SELECT COUNT(*) FROM accounts WHERE id IN (?, ?)",
            (sender_id, receiver_id))
        if cursor.fetchone()[0] != 2:
            raise TransferError("один из счетов не существует")
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def demo() -> None:
    """Демонстрация commit и rollback."""
    connection = sqlite3.connect(":memory:")
    init_db(connection)
    print("Начальные счета:", get_balances(connection))

    transfer(connection, 1, 2, 30)
    print("Успешный перевод 30: commit, счета:",
          get_balances(connection))

    print("Перевод 500 (больше баланса):")
    try:
        transfer(connection, 1, 2, 500)
    except sqlite3.IntegrityError as error:
        print(f"  IntegrityError: {error}")
    print("  rollback: счета не изменились:",
          get_balances(connection))

    print("Перевод на несуществующий счёт 999:")
    try:
        transfer(connection, 1, 999, 10)
    except TransferError as error:
        print(f"  TransferError: {error}")
    print("  rollback: счета не изменились:",
          get_balances(connection))
    connection.close()


if __name__ == "__main__":
    demo()
