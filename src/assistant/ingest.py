from . import database
from .retrieval import build_index


def main():
    chunk_count = build_index()
    database.ensure_database()
    print(f"Indexed {chunk_count} document chunks and prepared the database.")


if __name__ == "__main__":
    main()
