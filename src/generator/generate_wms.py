import os
import random

import mysql.connector
from dotenv import load_dotenv


load_dotenv()

MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": "fulfillment_wms",
}

SEED = 42

WAREHOUSE_COUNT = 50
INVENTORY_COUNT = 100_000
EVENT_COUNT = 500_000

REGIONS = [
    "South Asia",
    "Southeast Asia",
    "North America",
    "Europe",
]

EVENT_TYPES = [
    "ORDER_RECEIVED",
    "ORDER_PICKED",
    "ORDER_PACKED",
    "ORDER_DISPATCHED",
]

EVENT_STATUSES = [
    "completed",
    "pending",
]


def generate_warehouses(connection):
    random.seed(SEED)

    warehouses = []

    for i in range(1, WAREHOUSE_COUNT + 1):
        region = random.choice(REGIONS)

        warehouses.append(
            (
                f"WH-{i:03d}",
                f"Warehouse {i:03d}",
                region,
                random.randint(10_000, 100_000),
            )
        )

    cursor = connection.cursor()

    cursor.executemany(
        """
        INSERT INTO warehouses
            (warehouse_code, warehouse_name, region, capacity_units)
        VALUES
            (%s, %s, %s, %s);
        """,
        warehouses,
    )

    cursor.close()

    return list(range(1, WAREHOUSE_COUNT + 1))


def generate_inventory(connection, warehouse_ids):
    random.seed(SEED + 1)

    inventory = []

    for _ in range(INVENTORY_COUNT):
        warehouse_id = random.choice(warehouse_ids)
        quantity_available = random.randint(0, 10_000)
        quantity_reserved = random.randint(
            0,
            min(quantity_available, 1_000),
        )

        inventory.append(
            (
                warehouse_id,
                f"PROD-{random.randint(1, 1000):04d}",
                quantity_available,
                quantity_reserved,
            )
        )

    cursor = connection.cursor()

    cursor.executemany(
        """
        INSERT INTO inventory
            (
                warehouse_id,
                product_id,
                quantity_available,
                quantity_reserved
            )
        VALUES
            (%s, %s, %s, %s);
        """,
        inventory,
    )

    cursor.close()

    return len(inventory)


def generate_fulfillment_events(connection, warehouse_ids):
    random.seed(SEED + 2)

    events = []

    for _ in range(EVENT_COUNT):
        events.append(
            (
                random.randint(1, 100_000),
                random.choice(warehouse_ids),
                random.choice(EVENT_TYPES),
                random.choice(EVENT_STATUSES),
            )
        )

    cursor = connection.cursor()

    cursor.executemany(
        """
        INSERT INTO fulfillment_events
            (
                order_id,
                warehouse_id,
                event_type,
                event_status
            )
        VALUES
            (%s, %s, %s, %s);
        """,
        events,
    )

    cursor.close()

    return len(events)


def main():
    connection = mysql.connector.connect(**MYSQL_CONFIG)

    try:
        print("Generating warehouses...")
        warehouse_ids = generate_warehouses(connection)
        connection.commit()
        print(f"Created {len(warehouse_ids):,} warehouses")

        print("Generating inventory...")
        inventory_count = generate_inventory(
            connection,
            warehouse_ids,
        )
        connection.commit()
        print(f"Created {inventory_count:,} inventory records")

        print("Generating fulfillment events...")
        event_count = generate_fulfillment_events(
            connection,
            warehouse_ids,
        )
        connection.commit()
        print(f"Created {event_count:,} fulfillment events")

    finally:
        connection.close()


if __name__ == "__main__":
    main()