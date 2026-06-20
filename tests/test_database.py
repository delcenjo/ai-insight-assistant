import pytest

from assistant import database


def make_db(tmp_path):
    db_path = tmp_path / "company.db"
    connection = database.connect(db_path=db_path)
    database.seed_company(connection)
    connection.close()
    return db_path


def test_employees_are_seeded(tmp_path):
    with database.connect(read_only=True, db_path=make_db(tmp_path)) as connection:
        rows = database.run_select(connection, "SELECT COUNT(*) AS n FROM employees")
    assert rows[0]["n"] == 25


def test_aggregation_query(tmp_path):
    with database.connect(read_only=True, db_path=make_db(tmp_path)) as connection:
        rows = database.run_select(
            connection,
            "SELECT department, COUNT(*) AS n FROM employees GROUP BY department ORDER BY n DESC",
        )
    assert rows[0]["department"] == "Engineering"
    assert rows[0]["n"] == 10


def test_rejects_write_statements(tmp_path):
    with database.connect(read_only=True, db_path=make_db(tmp_path)) as connection:
        with pytest.raises(ValueError):
            database.run_select(connection, "DELETE FROM employees")
