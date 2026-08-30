# Architecture Decisions

## Business Context

A fictional multi-regional fulfillment and logistics operator is building a unified
operational data platform across warehouse, inventory, transportation, and
connected-device systems.

## Source Systems

### Order Management System (OMS)
Owns customers, orders, and payments.

### Warehouse Management System (WMS)
Owns warehouses, inventory, and fulfillment operations.

### Transportation Management System (TMS)
Owns shipments, carriers/vehicles, and transportation operations.

### Device / Telemetry Platform
Owns connected devices and operational telemetry.

## Source Database Distribution

PostgreSQL:
- OMS
- WMS

MySQL:
- TMS
- Device / Telemetry

The heterogeneous database setup intentionally simulates an enterprise environment
where operational systems may use different database technologies.

## Streaming vs Batch

Not all data requires streaming.

Operational events where low latency matters will eventually flow through CDC and
Kafka.

Reference and non-time-sensitive data can be processed through batch workflows.

## Future Architecture

The platform will evolve incrementally:

1. Synthetic source data
2. CDC and streaming
3. AWS landing and warehouse
4. Batch orchestration and dbt
5. Data quality, observability, and CI/CD
6. AI agent / MCP operational investigation layer
7. Lakehouse extension

## Initial Data Model

The initial model represents the operational systems rather than the final
analytical model. Source-system structure is intentionally preserved so that
the data platform must integrate heterogeneous operational data before
creating analytical models.

### Order Management System (OMS)

- `customers` — customer master information
- `orders` — customer orders and their lifecycle state
- `payments` — payment transactions associated with orders

### Warehouse Management System (WMS)

- `warehouses` — fulfillment facilities and their attributes
- `inventory` — inventory state by warehouse
- `fulfillment_events` — operational events occurring during fulfillment

### Transportation Management System (TMS)

- `shipments` — packages moving through the transportation network
- `vehicles` — transportation assets
- `transportation_events` — shipment and transportation lifecycle events

### Device / Telemetry Platform

- `devices` — connected operational devices
- `device_events` — device health, readings, and operational events

### Entity Relationships

The initial business relationships are:

```
Customer
   │
   └──< Orders
           │
           ├──< Payments
           │
           └──< Fulfillment Events
                       │
                       └── Warehouse
                              │
                              └── Inventory

Order
   │
   └── Shipment ──< Transportation Events >── Vehicle

Warehouse
   │
   └── Devices
          │
          └── Device Events

```

### Phase 0 Modeling Constraint

For initial development, each order contains a single product and results in
a single shipment. This deliberately reduces relational complexity while the
ingestion and event architecture is being established.

The model may later be extended to support multi-item orders, split
shipments, partial fulfillment, returns, and other operational scenarios.

### Operational Model vs Analytical Model

This is an operational source model, not a star schema.

The analytical layer will be designed separately after ingestion and
integration. Source data will retain its original operational semantics,
while downstream transformation may produce dimensional/fact models for
analytics and reporting.