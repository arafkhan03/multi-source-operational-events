import os

import psycopg
import yaml
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

server = MCPServer(
    name="fulfillment-analytics",
    version="1.0.0",
    instructions=(
        "Governed analytics access for the fulfillment platform. "
        "Only the analytics schema is available."
    ),
)


@server.tool()
def get_semantic_layer() -> str:
    """Return the governed analytics semantic layer."""

    with open("ai/semantic_layer.yaml", "r", encoding="utf-8") as file:
        return file.read()


@server.tool()
def execute_analytics_query(sql: str) -> str:
    """Execute a read-only query against the governed analytics schema."""

    sql = sql.strip().rstrip(";")
    lowered_sql = sql.lower()

    if not lowered_sql.startswith(("select", "with")):
        raise ValueError("Only SELECT/WITH queries are allowed.")

    forbidden = (
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "truncate",
        "grant",
        "revoke",
    )

    if any(word in lowered_sql.split() for word in forbidden):
        raise ValueError("Unsafe SQL detected.")

    if "analytics." not in lowered_sql:
        raise ValueError("Only the governed analytics schema is allowed.")

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)

            columns = [description.name for description in cursor.description]
            rows = cursor.fetchall()

    return yaml.safe_dump(
        {
            "columns": columns,
            "rows": [list(row) for row in rows],
        },
        sort_keys=False,
    )


if __name__ == "__main__":
    server.run()