Полошков Ярослав Витальевич, группа 220042-11, вариант 4, лабораторная №7

# Лабораторная работа №7. Работа с различными СУБД в Python

Дисциплина: «Методы и технологии программирования» (часть 1).

**Цель работы:** научиться работать с базами данных из Python:
sqlite3, SQLAlchemy ORM.

Окружение: Python 3.11.1, Windows, sqlite3 (стандартная библиотека),
SQLAlchemy 2.1 (`pip install -r requirements.txt`). Все программы
работают на in-memory базах — прогон воспроизводим и не оставляет
файлов БД.

## Задания варианта 4

По таблице индивидуальных вариантов (строка «4»: `4 6 10 | 5 9`):

| Сложность | № | Задание | Файл |
|-----------|---|---------|------|
| Средняя | 4 | Обновить запись | [`task04_update_record.py`](task04_update_record.py) |
| Средняя | 8 | Выполнить JOIN | [`task08_join.py`](task08_join.py) |
| Средняя | 10 | Использовать SQLAlchemy для одной таблицы | [`task10_sqlalchemy_table.py`](task10_sqlalchemy_table.py) |
| Повышенная | 4 | Индексация и поиск | [`advanced04_index_search.py`](advanced04_index_search.py) |
| Повышенная | 10 | Unit-тесты базы данных | [`advanced10_db_tests.py`](advanced10_db_tests.py) |

Протокол фактических запусков — в [`demo_output.txt`](demo_output.txt).

---

## Средняя сложность

### Задание 4. Обновить запись

`update_grade` выполняет параметризованный `UPDATE students SET grade
= ? WHERE id = ?` (плейсхолдеры исключают SQL-инъекцию) и возвращает
`rowcount`: 1 — запись обновлена, 0 — такого id нет. Запись
фиксируется через `with connection:` (коммит при успехе, rollback
при исключении). Оценка валидируется и в Python, и на уровне схемы
(`CHECK (grade BETWEEN 2 AND 5)`).

```
До UPDATE:    (1, 'Полошков Ярослав Витальевич', '220042-11', 4)
UPDATE students SET grade = 5 WHERE id = 1; изменено строк: 1
После UPDATE: (1, 'Полошков Ярослав Витальевич', '220042-11', 5)
UPDATE несуществующего id=999: 0 строк изменено
```

### Задание 8. Выполнить JOIN

Две связанные таблицы: `groups` и `students` (внешний ключ
`group_id REFERENCES groups(id)`). `INNER JOIN` выводит студентов
вместе с названием группы и факультетом; `LEFT JOIN + GROUP BY`
считает число студентов и средний балл по группам, включая группу
без студентов (`total = 0`, `avg_grade = NULL`).

```
LEFT JOIN + GROUP BY (статистика по группам):
   ('220042-11', 2, 4.5)
   ('221341', 1, 5.0)
   ('229999', 0, None)
```

### Задание 10. Использовать SQLAlchemy для одной таблицы

ORM SQLAlchemy 2.0 (декларативный стиль) для таблицы `books`:
модель `Book`, функции `add_book`, `get_books` (фильтр по автору),
`update_year`, `delete_book`. Сессии через `with Session(engine)`,
после коммита — `refresh` + `expunge`, несуществующий id даёт
`LookupError`. Предметная область отличается от лабы №6 (там
`students`, здесь `books`).

```
INSERT: 3 книги
SELECT по автору 'Роберт Мартин': [Book(id=1, 'Чистый код', ...)]
UPDATE: год книги id=1 теперь 2019
DELETE: осталось книг: 2
```

---

## Повышенная сложность

### Задание 4. Индексация и поиск

Таблица на 5000 детерминированных записей. Префиксный поиск реализован
диапазонным запросом `full_name >= ? AND full_name < ?` вместо
`LIKE 'prefix%'`: SQLite не применяет индекс к LIKE с bound-параметром,
а диапазонный запрос после `CREATE INDEX idx_students_name` выполняется
как **SEARCH по покрывающему индексу**. План проверяется через
`EXPLAIN QUERY PLAN`, время замеряется `perf_counter` по 50 прогонам:

```
Без индекса: план ['SCAN students'], 0.390 мс/запрос
С индексом:  план ['SEARCH students USING COVERING INDEX
idx_students_name (full_name>? AND full_name<?)'], 0.009 мс/запрос
```

Тесты дополнительно проверяют, что результаты поиска с индексом и без
совпадают в точности.

### Задание 10. Unit-тесты базы данных

`advanced10_db_tests.py` — самостоятельный набор из 13 unittest для
всех DB-модулей: обновление записи (rowcount 0/1, валидация,
персистентность), JOIN (строки INNER JOIN, пустая группа в LEFT JOIN,
целостность внешнего ключа), ORM (CRUD, фильтр, LookupError,
валидация). Каждый тест получает свежую in-memory базу в `setUp` —
тесты изолированы и порядок их выполнения не важен.

```
$ py -3 -m unittest advanced10_db_tests -v
...
Ran 13 tests in 0.041s

OK
```

---

## Проверка качества

### Все тесты репозитория

```
$ py -3 -m unittest test_tasks advanced10_db_tests -v
...
Ran 19 tests in 0.045s

OK
```

13 тестов БД (`advanced10_db_tests.py`) + 6 тестов индексации
(`test_tasks.py`): план SCAN без индекса, SEARCH с индексом,
идентичность результатов, отсутствие совпадений.

### Соответствие PEP8

```
$ py -3 -m flake8 .
(команда не вывела ни одной строки)
код возврата: 0
```

Строки не длиннее 79 символов, docstring у каждого модуля, класса и
функции, аннотации типов, параметризованные SQL-запросы.

## Структура репозитория

| Файл | Назначение |
|------|------------|
| `README.md` | Данные студента (первая строка) и отчёт по заданиям |
| `task04_update_record.py` | Задание 4 (средняя): UPDATE с rowcount |
| `task08_join.py` | Задание 8 (средняя): INNER/LEFT JOIN |
| `task10_sqlalchemy_table.py` | Задание 10 (средняя): ORM для books |
| `advanced04_index_search.py` | Задание 4 (повышенная): индекс, EXPLAIN, замеры |
| `advanced10_db_tests.py` | Задание 10 (повышенная): 13 unit-тестов БД |
| `test_tasks.py` | 6 тестов индексации и поиска |
| `demo_output.txt` | Протокол запусков, тестов и flake8 |
| `collect_demo.py` | Скрипт сбора протокола |
| `requirements.txt` | SQLAlchemy (sqlite3 — встроен) |
| `.gitignore` | Исключения Python-проекта и `*.db` |

## Как запустить

```bash
pip install -r requirements.txt

python task04_update_record.py
python task08_join.py
python task10_sqlalchemy_table.py
python advanced04_index_search.py

python -m unittest test_tasks advanced10_db_tests -v   # все тесты
python -m flake8 .                                     # стиль
python collect_demo.py                                 # протокол
```

Работа велась в feature-ветках, каждая слита в `main` merge-коммитом
(`--no-ff`). Сообщения коммитов — по Conventional Commits.
