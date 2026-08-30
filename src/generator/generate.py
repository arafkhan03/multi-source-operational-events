import os
import random

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SEED = 42

CUSTOMER_COUNT = 10_000
ORDER_COUNT = 100_000


FIRST_NAMES = [
    "Rahim",
    "Sarah",
    "Michael",
    "Aisha",
    "Daniel",
    "Fatima",
    "James",
    "Sofia",
    "Ahmed",
    "Emma",
]

LAST_NAMES = [
    "Ahmed",
    "Chen",
    "Brown",
    "Khan",
    "Wilson",
    "Rahman",
    "Smith",
    "Garcia",
    "Taylor",
    "Lee",
]

REGIONS = [
    "South Asia",
    "Southeast Asia",
    "North America",
    "Europe",
]

CUSTOMER_TIERS = [
    "standard",
    "premium",
]

ORDER_STATUSES = [
    "placed",
    "confirmed",
    "cancelled",
]

PAYMENT_STATUSES = [
    "completed",
    "pending",
    "failed",
]

CURRENCIES = [
    "USD",
    "EUR",
    "SGD",
]

PAYMENT_METHODS = [
    "card",
    "bank_transfer",
    "wallet",
]


def generate_customers(connection):
    random.seed(SEED)

    customers = []

    for _ in range(CUSTOMER_COUNT):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        customers.append(
            (
                f"{first_name} {last_name}",
                f"{first_name.lower()}.{last_name.lower()}.{random.randint(1, 999999)}@example.com",
                random.choice(REGIONS),
                random.choice(CUSTOMER_TIERS),
            )
        )

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO oms.customers
                (customer_name, email, region, customer_tier, created_at, updated_at)
            VALUES
                (%s, %s, %s, %s, NOW(), NOW());
            """,
            customers,
        )

        cursor.execute(
            """
            SELECT customer_id
            FROM oms.customers
            ORDER BY customer_id DESC
            LIMIT %s;
            """,
            (CUSTOMER_COUNT,),
        )

        customer_ids = [row[0] for row in cursor.fetchall()]

    return customer_ids


def generate_orders(connection, customer_ids):
    random.seed(SEED + 1)

    orders = []

    for _ in range(ORDER_COUNT):
        orders.append(
            (
                random.choice(customer_ids),
                f"PROD-{random.randint(1, 1000):04d}",
                random.randint(1, 5),
                random.choice(ORDER_STATUSES),
                random.choice(REGIONS),
            )
        )

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO oms.orders
                (customer_id, product_id, quantity, order_status, order_region, created_at, updated_at)
            VALUES
                (%s, %s, %s, %s, %s, NOW(), NOW());
            """,
            orders,
        )

        cursor.execute(
            """
            SELECT order_id
            FROM oms.orders
            ORDER BY order_id DESC
            LIMIT %s;
            """,
            (ORDER_COUNT,),
        )

        order_ids = [row[0] for row in cursor.fetchall()]

    return order_ids


def generate_payments(connection, order_ids):
    random.seed(SEED + 2)

    payments = []

    for order_id in order_ids:
        payments.append(
            (
                order_id,
                random.choice(PAYMENT_STATUSES),
                round(random.uniform(20, 500), 2),
                random.choice(CURRENCIES),
                random.choice(PAYMENT_METHODS),
            )
        )

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO oms.payments
                (order_id, payment_status, amount, currency, payment_method, created_at, updated_at)
            VALUES
                (%s, %s, %s, %s, %s, NOW(), NOW());
            """,
            payments,
        )

    return len(payments)


def main():
    with psycopg.connect(DATABASE_URL) as connection:
        print("Generating customers...")
        customer_ids = generate_customers(connection)
        print(f"Created {len(customer_ids):,} customers")

        print("Generating orders...")
        order_ids = generate_orders(connection, customer_ids)
        print(f"Created {len(order_ids):,} orders")

        print("Generating payments...")
        payment_count = generate_payments(connection, order_ids)
        print(f"Created {payment_count:,} payments")


if __name__ == "__main__":
    main()