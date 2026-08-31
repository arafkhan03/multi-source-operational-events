import os
import re

import ollama
import psycopg
import yaml
from flask import Flask, render_template_string, request


app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL = "llama3.2:3b"


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Fulfillment Analytics AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 50px auto;
            padding: 0 20px;
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }

        textarea {
            width: 100%;
            height: 100px;
            padding: 12px;
            font-size: 16px;
            box-sizing: border-box;
        }

        button {
            margin-top: 10px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }

        .section {
            margin-top: 30px;
        }

        pre {
            background: #f4f4f4;
            padding: 15px;
            overflow-x: auto;
        }

        .answer {
            font-size: 20px;
            padding: 20px;
            background: #f7f7f7;
        }

        .error {
            color: darkred;
            background: #ffecec;
            padding: 15px;
        }
    </style>
</head>

<body>

<h1>Fulfillment Analytics AI</h1>
<div class="subtitle">
    Governed analytics assistant
</div>

<form method="POST">
    <textarea
        name="question"
        placeholder="Ask a business question..."
        required
    >{{ question }}</textarea>

    <br>

    <button type="submit">Ask</button>
</form>

{% if answer %}
<div class="section">
    <h2>Answer</h2>
    <div class="answer">{{ answer }}</div>
</div>
{% endif %}

{% if sql %}
<div class="section">
    <h2>Generated SQL</h2>
    <pre>{{ sql }}</pre>
</div>
{% endif %}

{% if error %}
<div class="section">
    <h2>Error</h2>
    <div class="error">{{ error }}</div>
</div>
{% endif %}

</body>
</html>
"""


def load_semantic_layer():
    with open("ai/semantic_layer.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_system_prompt(semantic_layer):
    return f"""
You are a data analyst assistant for a fulfillment platform.

Generate PostgreSQL SQL for business questions.

STRICT RULES:

1. Only query the analytics schema.
2. Never query the oms schema.
3. Use ONLY the views and columns listed below.
4. Do not invent tables, views, columns, schemas, or aliases.
5. Do not prefix columns with invented names.
6. Generate READ-ONLY SQL only.
7. Return ONLY the complete SQL query.
8. Return the complete query on ONE SINGLE LINE.

AVAILABLE VIEWS:

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

SQL:
SELECT SUM(payment_count) FROM analytics.payment_summary;

Question:
Which payment method has the highest number of completed payments?

SQL:
SELECT payment_method, SUM(payment_count) AS payment_count FROM analytics.payment_summary WHERE payment_status = 'completed' GROUP BY payment_method ORDER BY payment_count DESC LIMIT 1;
"""


def generate_sql(question):
    semantic_layer = load_semantic_layer()

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(semantic_layer),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    sql = response["message"]["content"].strip()

    sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"^```\s*", "", sql)
    sql = re.sub(r"\s*```$", "", sql)

    sql = sql.strip().rstrip(";")

    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT/WITH queries are allowed.")

    if "analytics." not in sql.lower():
        raise ValueError("Only the governed analytics schema is allowed.")

    if re.search(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE)\b",
        sql,
        re.IGNORECASE,
    ):
        raise ValueError("Unsafe SQL detected.")

    return sql


def execute_sql(sql):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)

            columns = [description.name for description in cursor.description]
            rows = cursor.fetchall()

    return columns, rows


def generate_answer(question, sql, columns, rows):
    result = {
        "columns": columns,
        "rows": [list(row) for row in rows],
    }

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are an executive data assistant.

Answer the business question using ONLY the supplied query result.
Do not invent facts.
Keep the answer concise and business-friendly.
""",
            },
            {
                "role": "user",
                "content": f"""
Question:
{question}

SQL:
{sql}

Result:
{result}
""",
            },
        ],
    )

    return response["message"]["content"]


@app.route("/", methods=["GET", "POST"])
def index():

    question = ""
    answer = ""
    sql = ""
    error = ""

    if request.method == "POST":

        question = request.form["question"]

        try:
            sql = generate_sql(question)

            columns, rows = execute_sql(sql)

            answer = generate_answer(
                question,
                sql,
                columns,
                rows,
            )

        except Exception as exc:
            error = str(exc)

    return render_template_string(
        HTML,
        question=question,
        answer=answer,
        sql=sql,
        error=error,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True,
    )