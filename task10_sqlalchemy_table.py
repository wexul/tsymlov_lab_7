"""Задание 10 (средняя сложность): SQLAlchemy для одной таблицы.

ORM SQLAlchemy 2.0 для таблицы books (библиотека): модель Book,
инициализация схемы, добавление, выборка с фильтром по автору,
обновление года, удаление. Предметная область отличается от лабы №6
(там была таблица students) - здесь книги.

Запуск: python task10_sqlalchemy_table.py
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)


class Base(DeclarativeBase):
    """Базовый класс декларативных моделей."""


class Book(Base):
    """Модель книги: таблица books."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        """Техническое представление книги."""
        return (f"Book(id={self.id}, {self.title!r}, "
                f"{self.author!r}, {self.year})")


def make_engine(url: str = "sqlite:///:memory:"):
    """Создаёт движок SQLAlchemy (по умолчанию in-memory)."""
    return create_engine(url, echo=False)


def init_db(engine) -> None:
    """Создаёт таблицу books."""
    Base.metadata.create_all(engine)


def add_book(engine, title: str, author: str, year: int) -> Book:
    """Добавляет книгу с валидацией полей."""
    if not title.strip():
        raise ValueError("название не может быть пустым")
    if not author.strip():
        raise ValueError("автор не может быть пустым")
    if not 0 <= year <= 2100:
        raise ValueError(f"некорректный год: {year}")
    with Session(engine) as session:
        book = Book(title=title.strip(), author=author.strip(),
                    year=year)
        session.add(book)
        session.commit()
        session.refresh(book)
        session.expunge(book)
        return book


def get_books(engine, author: str | None = None) -> list[Book]:
    """Возвращает книги, опционально фильтруя по автору."""
    statement = select(Book).order_by(Book.id)
    if author is not None:
        statement = statement.where(Book.author == author)
    with Session(engine) as session:
        return list(session.scalars(statement).all())


def update_year(engine, book_id: int, year: int) -> Book:
    """Обновляет год издания книги по id."""
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise LookupError(f"книга с id={book_id} не найдена")
        book.year = year
        session.commit()
        session.refresh(book)
        session.expunge(book)
        return book


def delete_book(engine, book_id: int) -> None:
    """Удаляет книгу по id."""
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise LookupError(f"книга с id={book_id} не найдена")
        session.delete(book)
        session.commit()


def demo() -> None:
    """Демонстрация CRUD для одной таблицы."""
    engine = make_engine()
    init_db(engine)
    first = add_book(engine, "Чистый код", "Роберт Мартин", 2008)
    add_book(engine, "Совершенный код", "Стив Макконнелл", 2004)
    add_book(engine, "Рефакторинг", "Мартин Фаулер", 1999)
    print("INSERT: 3 книги")
    print("SELECT все:", *get_books(engine), sep="\n  ")
    print("SELECT по автору 'Роберт Мартин':",
          get_books(engine, author="Роберт Мартин"))
    updated = update_year(engine, first.id, 2019)
    print(f"UPDATE: год книги id={first.id} теперь {updated.year}")
    delete_book(engine, first.id)
    print(f"DELETE: осталось книг: {len(get_books(engine))}")


if __name__ == "__main__":
    demo()
