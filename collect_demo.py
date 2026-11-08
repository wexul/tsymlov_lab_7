"""Собирает demo_output.txt реальными прогонами программ репозитория."""

import datetime
import subprocess

SEP = "-" * 70
out = []
out.append("Лабораторная работа №7, вариант 4 - фактические запуски "
           "программ")
out.append("=" * 70)
out.append("")
out.append("Дата выполнения: " + datetime.date.today().strftime("%d.%m.%Y"))
out.append("Python: 3.11.1, sqlite3, SQLAlchemy 2.1, aiosqlite 0.22")
out.append("ОС: Windows 10")
out.append("")
out.append("Все программы работают на in-memory базах SQLite, поэтому")
out.append("прогон полностью воспроизводим и не оставляет файлов БД.")
out.append("Каждый раздел: команда запуска, вывод, код возврата.")
out.append("")


def run(title, cmd):
    res = subprocess.run(cmd, capture_output=True, text=True,
                         encoding="utf-8")
    out.append(SEP)
    out.append(title)
    out.append(SEP)
    out.append("$ " + " ".join(cmd))
    out.append("")
    if res.stdout.strip():
        out.append(res.stdout.rstrip("\n"))
    if res.stderr.strip():
        out.append(res.stderr.rstrip("\n"))
    out.append("")
    out.append(f"код возврата: {res.returncode}")
    out.append("")


run("Задание 4 (средняя). Обновление записи (sqlite3 UPDATE)",
    ["py", "-3", "task04_update_record.py"])
run("Задание 6 (средняя). Параметры запроса и SQL-инъекция",
    ["py", "-3", "task06_parameterized_queries.py"])
run("Задание 10 (средняя). SQLAlchemy ORM для одной таблицы",
    ["py", "-3", "task10_sqlalchemy_table.py"])
run("Задание 5 (повышенная). Транзакции: commit и rollback",
    ["py", "-3", "advanced05_transactions.py"])
run("Задание 9 (повышенная). Асинхронный CRUD через aiosqlite",
    ["py", "-3", "advanced09_async_db.py"])
run("Дополнительно. INNER JOIN и LEFT JOIN + GROUP BY",
    ["py", "-3", "task08_join.py"])
run("Дополнительно. Индексация и поиск (EXPLAIN QUERY PLAN)",
    ["py", "-3", "advanced04_index_search.py"])
run("Дополнительно. Unit-тесты базы данных",
    ["py", "-3", "-m", "unittest", "advanced10_db_tests", "-v"])
run("Все модульные тесты репозитория",
    ["py", "-3", "-m", "unittest", "test_tasks", "advanced10_db_tests",
     "test_advanced_new", "-v"])
run("Проверка стиля кода (flake8)",
    ["py", "-3", "-m", "flake8", ".", "--statistics"])

with open("demo_output.txt", "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(out).rstrip("\n") + "\n")
print("demo_output.txt записан, строк:", len(out))
