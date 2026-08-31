import os
import re

import ollama
import psycopg
import yaml
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL = "llama3.2:3b"


def load_semantic_layer():
    with open("ai/semantic_layer.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_system_prompt(semantic_layer):
    return f"""
You are a data analyst assistant for a fulfillment platform.

Your job is to generate PostgreSQL SELECT queries for business questions.

STRICT RULES:

1. Only query the analytics schema.
2. Never query the oms schema.
3. Use ONLY the views and columns listed below.
4. Do NOT invent tables, views, columns, schemas, or aliases.
5. Do NOT use table aliases unless absolutely necessary.
6. When selecting a column, use the exact column name.
7. Do NOT prefix columns with invented names such as metrics., data., summary., etc.
8. For total counts, use COUNT(*) or SUM() as appropriate.
9. Generate PostgreSQL-compatible SQL.
10. Generate READ-ONLY SQL only.
11. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, or REVOKE.
12. Return ONLY the SQL query.
13. Do NOT return explanations.
14. Do NOT wrap the SQL in Markdown code fences.

GOVERNED SEMANTIC LAYER:

{yaml.dump(semantic_layer, sort_keys=False)}

AVAILABLE VIEWS AND COLUMNS:

analytics.customer_summary
- customer_id
- customer_name
- region
- customer_tier
- order_count
- completed_or_active_order_count
- completed_payment_value
- last_order_at

analytics.payment_summary
- payment_status
- currency
- payment_method
- payment_count
- total_amount
- average_payment_amount

EXAMPLE:

Question:
What is the total number of payments?

Correct SQL:
SELECT SUM(payment_count)
FROM analytics.payment_summary;

Question:
Which payment method has the highest number of completed payments?

Correct SQL:
SELECT payment_method, SUM(payment_count) AS payment_count
FROM analytics.payment_summary
WHERE payment_status = 'completed'
GROUP BY payment_method
ORDER BY payment_count DESC
LIMIT 1;
"""


def clean_sql(sql):
    sql = sql.strip()

    # Remove Markdown code fences if the model ignores the instruction.
    sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"^```\s*", "", sql)
    sql = re.sub(r"\s*```$", "", sql)

    return sql.strip().rstrip(";")


def validate_sql(sql):
    sql = clean_sql(sql)

    print("\nRAW MODEL OUTPUT:")
    print(repr(sql))

    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise ValueError(
            f"Only SELECT/WITH queries are allowed. Model returned: {sql!r}"
        )

    if re.search(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE)\b",
        sql,
        re.IGNORECASE,
    ):
        raise ValueError("Unsafe SQL detected.")

    if "analytics." not in sql.lower():
        raise ValueError("Query must use the governed analytics schema.")

    if re.search(
        r"\b(oms|public)\.",
        sql,
        re.IGNORECASE,
    ):
        raise ValueError("Query references a non-governed schema.")

    return sql


def generate_sql(question, semantic_layer):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(semantic_layer)
                + """
IMPORTANT OUTPUT FORMAT:
Return the COMPLETE SQL query on ONE SINGLE LINE.
The query MUST contain the analytics schema and table name.
Do not stop after SELECT.
Do not output anything except the complete SQL query.
""",
            },
            {
                "role": "user",
                "content": f"""
Generate one complete SQL query for this business question:

{question}
""",
            },
        ],
    )

    sql = response["message"]["content"]

    return validate_sql(sql)


def execute_sql(sql):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)

            columns = [description.name for description in cursor.description]
            rows = cursor.fetchall()

    return columns, rows


def explain_result(question, sql, columns, rows):
    result = {
        "columns": columns,
        "rows": rows,
    }

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are an executive data assistant.

Explain query results clearly and concisely.

Rules:
- Only use information contained in the supplied query result.
- Do not invent facts.
- Do not introduce unsupported explanations.
- If the result is empty, say that no matching data was found.
- Keep the answer concise.
""",
            },
            {
                "role": "user",
                "content": f"""
Business question:
{question}

SQL executed:
{sql}

Query result:
{result}

Give a concise business answer.
""",
            },
        ],
    )

    return response["message"]["content"]


def main():
    semantic_layer = load_semantic_layer()

    print("Fulfillment Platform AI Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ")

        if question.lower() == "exit":
            break

        try:
            sql = generate_sql(question, semantic_layer)

            print("\nGenerated SQL:")
            print(sql)

            columns, rows = execute_sql(sql)

            print("\nAnswer:")
            print(explain_result(question, sql, columns, rows))
            print()

        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()