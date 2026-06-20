import sqlite3

from .config import DB_PATH

FORBIDDEN_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", "create",
    "replace", "attach", "detach", "pragma", "vacuum", "reindex",
}

SCHEMA = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL,
    salary INTEGER NOT NULL,
    hire_date TEXT NOT NULL
);
"""

EMPLOYEES = [
    ("Ana Ruiz", "Engineering", "Senior Engineer", 62000, "2020-03-15"),
    ("Luis Gomez", "Engineering", "Engineer", 48000, "2021-06-01"),
    ("Marta Soler", "Engineering", "Engineer", 47000, "2022-01-10"),
    ("Carlos Vidal", "Engineering", "Staff Engineer", 75000, "2019-09-23"),
    ("Sofia Marin", "Engineering", "Engineer", 46000, "2022-09-05"),
    ("Diego Pena", "Engineering", "Senior Engineer", 60000, "2020-11-30"),
    ("Elena Cano", "Engineering", "Engineering Manager", 82000, "2019-04-12"),
    ("Pablo Ortiz", "Engineering", "Junior Engineer", 38000, "2023-02-20"),
    ("Lucia Ramos", "Engineering", "Engineer", 49000, "2021-10-18"),
    ("Mario Gil", "Engineering", "Junior Engineer", 37000, "2023-07-03"),
    ("Nora Vega", "Sales", "Account Executive", 45000, "2021-03-08"),
    ("Ivan Mora", "Sales", "Sales Manager", 70000, "2019-08-19"),
    ("Clara Sanz", "Sales", "Account Executive", 44000, "2022-04-25"),
    ("Hugo Diaz", "Sales", "Sales Development Rep", 35000, "2023-01-15"),
    ("Sara Luna", "Sales", "Account Executive", 46000, "2021-12-02"),
    ("Jorge Pla", "Support", "Support Lead", 52000, "2020-05-11"),
    ("Eva Roca", "Support", "Support Agent", 34000, "2022-06-14"),
    ("Raul Nieto", "Support", "Support Agent", 33000, "2023-03-09"),
    ("Lola Vera", "Support", "Support Agent", 34000, "2022-11-21"),
    ("Tomas Rey", "Marketing", "Marketing Manager", 65000, "2020-02-17"),
    ("Irene Mas", "Marketing", "Content Specialist", 42000, "2022-08-30"),
    ("Bruno Calvo", "Marketing", "Designer", 44000, "2021-07-12"),
    ("Paula Ferrer", "HR", "HR Manager", 63000, "2019-10-05"),
    ("Adrian Lozano", "HR", "Recruiter", 41000, "2022-03-22"),
    ("Nuria Pardo", "HR", "HR Generalist", 43000, "2021-05-19"),
]


def connect(read_only=False, db_path=DB_PATH):
    if read_only:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def list_tables(connection):
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return [row["name"] for row in rows]


def run_select(connection, query, max_rows=50):
    statement = query.strip().rstrip(";").strip()
    if not statement:
        raise ValueError("Empty query.")
    if ";" in statement:
        raise ValueError("Only a single statement is allowed.")
    tokens = statement.lower().split()
    if tokens[0] not in {"select", "with"}:
        raise ValueError("Only SELECT queries are allowed.")
    if FORBIDDEN_KEYWORDS.intersection(tokens):
        raise ValueError("Query contains a forbidden keyword.")
    return [dict(row) for row in connection.execute(statement).fetchmany(max_rows)]


def seed_company(connection):
    connection.executescript(SCHEMA)
    rows = [(i, *employee) for i, employee in enumerate(EMPLOYEES, start=1)]
    connection.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", rows)
    connection.commit()


def ensure_database(db_path=DB_PATH):
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = connect(db_path=db_path)
        seed_company(connection)
        connection.close()
