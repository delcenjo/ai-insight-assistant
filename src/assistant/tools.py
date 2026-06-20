import json

from . import database
from .config import TOP_K
from .retrieval import Retriever


class Toolbox:
    DEFINITIONS = [
        {
            "name": "search_docs",
            "description": (
                "Search the company handbook and internal documentation for relevant "
                "passages. Use for questions about policies, processes and guidelines."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "query_database",
            "description": (
                "Run a read-only SQL SELECT over the company database. Use for questions "
                "about employees, departments, salaries and counts. "
                "Table: employees(id, name, department, role, salary, hire_date)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    ]

    def __init__(self):
        self._retriever = None

    def execute(self, name, arguments):
        try:
            if name == "search_docs":
                return json.dumps(self._retriever_instance().search(arguments["query"], TOP_K))
            if name == "query_database":
                with database.connect(read_only=True) as connection:
                    return json.dumps(database.run_select(connection, arguments["query"]), default=str)
            return f"Error: unknown tool '{name}'"
        except Exception as error:
            return f"Error: {error}"

    def _retriever_instance(self):
        if self._retriever is None:
            self._retriever = Retriever()
        return self._retriever
