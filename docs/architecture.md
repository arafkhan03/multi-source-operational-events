# Architecture

## 1. Business Context

This project simulates a multi-regional fulfillment and logistics company operating across multiple operational systems.

The business needs a unified data platform capable of supporting:

* Operational reporting
* Executive KPI analysis
* Cross-system analytics
* Near-real-time operational events
* Governed AI-assisted data investigation

The core engineering challenge is not simply storing data. It is integrating heterogeneous operational systems into a governed platform that can reliably serve different downstream consumers.

---

## 2. Source Systems

The simulated enterprise contains four operational domains.

### Order Management System — OMS

Owns:

* Customers
* Orders
* Payments

Database:

**PostgreSQL**

### Warehouse Management System — WMS

Owns:

* Warehouses
* Inventory
* Fulfillment events

Database:

**MySQL**

### Transportation Management System — TMS

Owns:

* Shipments
* Vehicles
* Transportation events

Database:

**MySQL**

### Device / Telemetry Platform

Owns:

* Devices
* Device events
* Operational telemetry

Database:

**MySQL**

The heterogeneous source setup intentionally represents a realistic enterprise environment where different operational systems may use different technologies.

---

## 3. High-Level Architecture

```text
                    OPERATIONAL SYSTEMS
                           │
          ┌────────────────┼────────────────┐
          │                │                │
        OMS              WMS              TMS / IoT
     PostgreSQL          MySQL              MySQL
          │                │                │
          └────────────────┼────────────────┘
                           │
                    CDC / Batch Ingestion
                           │
                    Kafka / Debezium
                           │
                           ▼
                     AWS S3 Landing
                           │
                           ▼
                    Data Warehouse
                      Amazon Redshift
                           │
                           ▼
                Analytical Transformation
                       dbt / SQL
                           │
                           ▼
                 Governed Semantic Layer
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        BI / Analytics            AI / MCP Layer
                                      │
                                      ▼
                              AI Applications
```

The local implementation reproduces the important architectural boundaries without requiring a full AWS deployment.

---

## 4. Streaming vs Batch

Not every dataset requires real-time processing.

### Streaming

CDC and Kafka are appropriate for operational events where low latency provides business value.

Examples:

* Order status changes
* Payment status changes
* Fulfillment events
* Shipment events
* Device events

The local implementation demonstrates PostgreSQL CDC using Debezium and Kafka.

### Batch

Batch processing is appropriate for:

* Reference data
* Historical data
* Large periodic loads
* Data that does not require immediate availability

The production architecture would combine both patterns rather than forcing every workload through streaming.

---

## 5. CDC Architecture

The local CDC path is:

```text
PostgreSQL
    │
    │ logical replication
    ▼
Debezium
    │
    ▼
Kafka
    │
    ▼
Downstream ingestion
```

Debezium captures changes from the PostgreSQL OMS database and publishes them as Kafka events.

The connector configuration is located at:

```text
infra/cdc/postgres-connector.json
```

The local infrastructure is defined in:

```text
infra/cdc/docker-compose.yml
```

---

## 6. Landing and Warehouse Architecture

In a production AWS implementation:

```text
Operational Sources
       │
       ▼
CDC / Batch
       │
       ▼
Amazon S3
       │
       ▼
Amazon Redshift
       │
       ▼
Analytical Models
```

S3 acts as the durable landing layer.

Redshift acts as the analytical warehouse.

This separation provides:

* Durable raw-data retention
* Replay capability
* Separation between ingestion and analytics
* Independent downstream processing
* Scalable analytical workloads

The local project uses PostgreSQL as the development environment for the analytical layer rather than requiring an AWS account.

---

## 7. Analytical Layer

Operational source schemas are not exposed directly to business consumers.

Instead, the platform creates governed analytical models.

For example:

```text
oms.customers
oms.orders
oms.payments
       │
       ▼
analytics.customer_summary
analytics.payment_summary
       │
       ▼
BI / AI consumers
```

The analytical layer converts operational structures into business-oriented representations.

Examples:

### `analytics.customer_summary`

One row per customer containing:

* Customer attributes
* Order count
* Active/completed order count
* Completed payment value
* Last order timestamp

### `analytics.payment_summary`

Aggregated payment activity by:

* Payment status
* Currency
* Payment method

This allows downstream consumers to work with business concepts rather than reconstructing operational joins themselves.

---

## 8. Governed Semantic Layer

The AI layer should not directly query operational tables.

The project therefore introduces:

```text
ai/semantic_layer.yaml
```

The semantic layer defines:

* Approved analytical models
* Business-facing dimensions
* Business-facing metrics
* Model descriptions
* Allowed schemas
* Forbidden schemas

Conceptually:

```text
                 Semantic Layer
                       │
          ┌────────────┴────────────┐
          │                         │
 customer_summary             payment_summary
          │                         │
          └────────────┬────────────┘
                       │
              AI / BI Consumers
```

This creates a governance boundary between raw operational data and AI consumers.

---

## 9. AI Query Architecture

The implemented local AI flow is:

```text
User
 │
 ▼
Chatbot UI
 │
 ▼
Local LLM
 │
 ▼
Governed SQL Generation
 │
 ▼
SQL Validation
 │
 ▼
analytics.* only
 │
 ▼
PostgreSQL
 │
 ▼
Result
 │
 ▼
Local LLM
 │
 ▼
Business Explanation
```

The important architectural principle is that the model does not receive unrestricted access to the operational database.

The generated SQL is validated before execution.

The validator enforces:

* `SELECT` / `WITH` queries only
* No write operations
* Use of the governed `analytics` schema
* Removal of markdown SQL wrappers
* Execution against the approved analytical layer

---

## 10. MCP Extension

MCP is positioned above the governed analytical layer rather than directly against operational databases.

Conceptually:

```text
                    AI Application
                          │
                    MCP Client
                          │
                          ▼
                    MCP Server
                    ┌─────┴─────┐
                    │           │
               SQL Tool     Metadata Tool
                    │           │
                    └─────┬─────┘
                          ▼
                 Governed Analytics
                          │
                          ▼
                     Redshift
```

The MCP server provides a standardized interface through which an AI application can discover and invoke approved capabilities.

The important boundary is:

```text
AI
 │
 ▼
MCP / governed tools
 │
 ▼
Semantic / analytical layer
 │
 ▼
Warehouse
```

rather than:

```text
AI
 │
 ▼
Raw operational database
```

This makes the AI integration more controllable, auditable, and reusable.

---

## 11. Agentic Investigation Architecture

Simple questions do not necessarily require an agent.

For example:

> "Which payment method has the most completed payments?"

can be answered through:

```text
Question
   ↓
SQL generation
   ↓
Governed query
   ↓
Result
```

A more complex investigation may require multiple tools and reasoning steps.

For example:

> "Why has our most important customer started ordering less?"

could require:

```text
Identify customer
       ↓
Retrieve customer metrics
       ↓
Compare historical ordering
       ↓
Analyze payment behavior
       ↓
Analyze fulfillment performance
       ↓
Analyze regional / product patterns
       ↓
Combine evidence
       ↓
Generate explanation
```

This is where an agentic architecture becomes useful.

The agent can orchestrate multiple governed tools rather than being given unrestricted database access.

---

## 12. Local vs Production Architecture

### Local

```text
PostgreSQL
   │
   ├── OMS
   └── Analytics models
          │
          ▼
       Ollama
          │
          ▼
      Chatbot / MCP
```

Supporting infrastructure:

* Python
* PostgreSQL
* Ollama
* Local LLM
* MCP
* YAML semantic layer

### Production

```text
Operational Systems
       │
       ▼
CDC / Batch
       │
       ▼
      S3
       │
       ▼
   Redshift
       │
       ▼
 dbt / Semantic Layer
       │
       ├──────────► BI
       │
       ▼
 AI / MCP Platform
       │
       ▼
 AI Applications / Agents
```

Cloud implementation would additionally introduce production concerns such as:

* IAM
* Secrets management
* Network isolation
* Encryption
* Monitoring
* Data cataloguing
* Query governance
* Cost controls
* Model access controls
* Audit logging

---

## 13. Why This Architecture

The architecture deliberately separates responsibilities.

### Operational databases

Optimized for application transactions.

### S3

Durable landing and historical data layer.

### Redshift

Optimized for analytical workloads.

### Analytical models

Convert operational structures into business-oriented datasets.

### Semantic layer

Defines what AI and business consumers are allowed to understand and query.

### MCP

Provides a standardized tool interface for AI applications.

### AI / Agents

Consume governed capabilities rather than directly accessing operational systems.

This separation reduces coupling and allows each layer to evolve independently.

---

## 14. Current Scope

The project intentionally distinguishes implementation from architectural design.

### Implemented locally

* Synthetic OMS data
* Synthetic WMS data
* PostgreSQL operational database
* CDC configuration
* Kafka
* Debezium
* Analytical models
* Governed semantic layer
* Local LLM integration
* SQL generation
* SQL validation
* AI chatbot
* MCP server
* Local web interface

### Architecturally demonstrated

* S3 landing architecture
* Redshift production architecture
* Multi-source enterprise integration
* AI/MCP consumption pattern
* Agentic investigation pattern
* Production cloud boundaries

### Production next step

* AWS deployment
* Full multi-source ingestion
* Production S3 ingestion
* Redshift deployment
* dbt production project
* Orchestration
* Production observability
* IAM and secrets management
* Production AI model integration
* Agent orchestration
* Expanded MCP tool ecosystem

The distinction is intentional: architectural knowledge is demonstrated without claiming that every production component was deployed in this portfolio project.
