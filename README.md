# Multi-Source Operational Data Platform

> **A production-oriented data platform for a multi-regional fulfillment operator — integrating operational systems through CDC and event streaming, landing data for analytics, creating governed business models, and exposing trusted data to BI and AI applications.**

## 🧰 Tech Stack

### Data Engineering

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge\&logo=apachekafka\&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-000000?style=for-the-badge\&logo=debezium\&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge\&logo=mysql\&logoColor=white)

### Analytics & Data Modeling

![SQL](https://img.shields.io/badge/SQL-336791?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Semantic Layer](https://img.shields.io/badge/Semantic%20Layer-6C63FF?style=for-the-badge\&logo=databricks\&logoColor=white)

### AI & Data Products

![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge\&logo=ollama\&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-5B5BF7?style=for-the-badge\&logo=anthropic\&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)

### Platform & Infrastructure

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge\&logo=amazonaws\&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge\&logo=amazons3\&logoColor=white)
![Amazon Redshift](https://img.shields.io/badge/Amazon%20Redshift-8C4FFF?style=for-the-badge\&logo=amazonredshift\&logoColor=white)

### Production Evolution

![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge\&logo=dbt\&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge\&logo=apacheairflow\&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge\&logo=githubactions\&logoColor=white)

---

## 🧭 Repository Navigation

If you have only **2 minutes** and want to skim the technical parts, start here:

**[Architecture](./docs/architecture.md)** → **[CDC](./infra/cdc/docker-compose.yml)** → **[Debezium](./infra/cdc/postgres-connector.json)** → **[Semantic Layer](./ai/semantic_layer.yaml)** → **[AI App](./ai/app/web_app.py)**

---

## 👋 Connect

If you'd like to discuss the architecture, data platforms, analytics engineering, or AI-enabled data products:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Araf%20Khan-0A66C2?style=for-the-badge\&logo=linkedin\&logoColor=white)](https://www.linkedin.com/in/arafkhan03)

[![Email](https://img.shields.io/badge/Email-Contact%20Me-EA4335?style=for-the-badge\&logo=gmail\&logoColor=white)](mailto:araf.khan03@gmail.com)

## 📑 Table of Contents
* [Tech Stack](#tech-stack)
* [Connect](#connect)
* [Business Scenario](#business-scenario)
* [Architecture](#architecture)
* [Why This Architecture](#why-this-architecture)
* [Current Implementation](#current-implementation)
* [Data Flow](#data-flow)
* [Governed Semantic Layer](#governed-semantic-layer)
* [AI Consumption](#ai-consumption)
* [AI / MCP Extension](#ai--mcp-extension)
* [Repository Navigation](#repository-navigation)
* [Running the Project](#running-the-project)
* [Example Questions](#example-questions)
* [Operational Model vs Analytical Model](#operational-model-vs-analytical-model)
* [Production Architecture](#production-architecture)
* [Engineering Trade-offs](#engineering-trade-offs)
* [What This Project Demonstrates](#what-this-project-demonstrates)
* [Project Evolution](#project-evolution)
* [Future Evolution](#future-evolution)
* [Project Status](#project-status)

## 30-Second Overview

A fictional multi-regional fulfillment and logistics company operates across **order management, warehouse operations, transportation, and connected devices**.

Its operational systems are optimized for transactions, not enterprise analytics.

The platform in this repository demonstrates how those systems can be connected into a governed data architecture that supports:

* operational data integration
* change data capture (CDC)
* event streaming
* analytical data modeling
* business-facing metrics
* governed AI consumption
* natural-language business questions

The design deliberately separates:

**operational systems → data platform → analytical consumption → AI applications**

so downstream consumers do not directly depend on transactional databases.

---

## Business Scenario

The company operates a distributed fulfillment network across multiple regions.

Its operational landscape contains:

| System          | Responsibility                             | Technology |
| --------------- | ------------------------------------------ | ---------- |
| OMS             | Customers, orders, payments                | PostgreSQL |
| WMS             | Warehouses, inventory, fulfillment         | MySQL      |
| TMS             | Shipments, vehicles, transportation events | MySQL      |
| Device Platform | Device state and telemetry                 | MySQL      |

The platform must bring these sources together while preserving their operational ownership.

### Business questions the platform should support

* How many orders are being placed?
* Where are payment failures concentrated?
* Which payment methods perform best?
* Which customers generate the most value?
* Which customers are becoming less active?
* How is fulfillment performing across warehouses?
* Where are operational bottlenecks emerging?
* How can business users safely ask these questions using natural language?

---

# Architecture

## Executive Architecture

```text
                         OPERATIONAL SYSTEMS
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
            OMS                WMS                TMS
       PostgreSQL             MySQL              MySQL
             │
             │ CDC
             ▼
          Debezium
             │
             ▼
           Kafka
             │
             ▼
       Landing / Lake
        S3 / MinIO
             │
             ▼
        Data Warehouse
        Redshift / Local
             │
             ▼
     Analytics / Semantic
           Models
             │
        ┌────┴─────┐
        │          │
        ▼          ▼
       BI       AI / MCP
                   │
                   ▼
             Business Users
```

The architecture is intentionally layered.

Each layer has a distinct responsibility:

### 1. Operational systems

Systems of record for business transactions.

### 2. CDC / streaming

Captures operational changes without requiring analytical workloads to query transactional databases directly.

### 3. Landing layer

Provides durable raw-data storage and decouples ingestion from downstream processing.

### 4. Warehouse

Provides a platform optimized for analytical workloads.

### 5. Analytics / semantic layer

Transforms technical source structures into governed business-facing concepts.

### 6. BI / AI

Consumes governed data rather than directly querying operational systems.

---

# Why this architecture?

The technologies are not selected simply because they are popular.

They solve different architectural problems.

| Decision         | Reason                                                                                 |
| ---------------- | -------------------------------------------------------------------------------------- |
| CDC              | Capture operational changes without tightly coupling analytics to source applications  |
| Kafka            | Decouple event producers from downstream consumers                                     |
| Object storage   | Durable and inexpensive landing layer                                                  |
| Warehouse        | Optimize analytical workloads                                                          |
| Analytics models | Convert operational structures into business-facing concepts                           |
| Semantic layer   | Establish governed definitions for downstream consumers                                |
| AI layer         | Allow natural-language access without exposing raw operational databases               |
| MCP              | Provide a standardized tool boundary between AI applications and governed capabilities |

The key principle is:

> **Consumers should depend on governed data products, not operational implementation details.**

---

# Current Implementation

This repository intentionally contains a **working vertical slice** rather than pretending to be a fully deployed enterprise cloud platform.

### 🟢 Implemented

* Synthetic OMS data generation
* Synthetic WMS data generation
* PostgreSQL operational database
* OMS relational model
* Debezium PostgreSQL connector
* Kafka
* CDC event capture
* Local object-storage architecture using MinIO
* Analytics views for customer/payment consumption
* Governed semantic layer
* Local Ollama LLM
* AI-generated SQL
* SQL safety validation
* AI result explanation
* Local chatbot UI
* MCP server exposing governed capabilities

### 🟡 Demonstrated / simulated locally

* AWS S3 landing architecture → represented locally with MinIO
* Redshift warehouse architecture → analytical layer demonstrated locally
* Cloud deployment architecture
* Batch orchestration
* dbt transformation workflow
* Data quality / observability architecture
* CI/CD architecture

### 🔵 Production evolution

A production implementation would replace local components with managed infrastructure and add:

* AWS S3
* Amazon Redshift
* managed Kafka / Amazon MSK
* Airflow / MWAA
* dbt
* automated data quality
* lineage
* centralized observability
* IAM/RBAC
* secrets management
* CI/CD
* schema evolution controls
* replay / recovery mechanisms
* AI authorization and audit controls
* stronger text-to-SQL evaluation

---

# Data Flow

## Operational Data

The initial OMS contains:

```text
oms.customers
oms.orders
oms.payments
```

The current synthetic dataset contains approximately:

```text
10,000 customers
100,000 orders
100,000 payments
```

The OMS maintains normal transactional relationships:

```text
Customer
   │
   └──< Orders
           │
           └──< Payments
```

The source model intentionally remains operational.

It is **not** the analytical model.

---

# CDC and Streaming

PostgreSQL changes are captured using Debezium.

```text
PostgreSQL
    │
    │ WAL / logical replication
    ▼
Debezium
    │
    ▼
Kafka
```

Kafka provides the event transport layer between source systems and downstream consumers.

The local development environment runs Kafka and Debezium using Docker.

This isolates infrastructure dependencies from the host machine and makes the environment reproducible.

---

# Analytics Layer

The analytical layer deliberately does not expose the raw OMS schema directly to consumers.

Instead, business-facing views are created.

### `analytics.customer_summary`

One row per customer containing:

* customer identity
* region
* customer tier
* order count
* completed/active order count
* completed payment value
* most recent order

### `analytics.payment_summary`

Payment activity aggregated by:

* payment status
* currency
* payment method

with metrics including:

* payment count
* total amount
* average payment amount

This creates a controlled boundary between operational data and downstream consumption.

---

# Governed Semantic Layer

The semantic layer is defined in:

```text
ai/semantic_layer.yaml
```

It describes:

* available business models
* dimensions
* metrics
* source views
* business definitions
* permitted schemas
* forbidden schemas

For example:

```text
analytics.customer_summary
analytics.payment_summary
```

are exposed to the AI layer.

The operational `oms` schema is explicitly forbidden.

This means the AI does not receive unrestricted access to the operational database.

---

# AI Consumption

The project demonstrates a local natural-language analytics interface.

```text
Business Question
       │
       ▼
Local LLM
(Ollama)
       │
       ▼
Governed Semantic Layer
       │
       ▼
Generated SQL
       │
       ▼
SQL Validation
       │
       ▼
Analytics Schema
       │
       ▼
PostgreSQL
       │
       ▼
Query Result
       │
       ▼
Executive Explanation
```

Example:

> **Which payment method has the highest number of completed payments?**

The model generates a query against the governed analytics model, the query is validated, executed, and the result is converted into a concise business answer.

---

# AI / MCP Extension

The MCP implementation demonstrates another possible consumption boundary:

```text
AI Application
      │
      ▼
     MCP
      │
 ┌────┴──────────────────┐
 │                       │
 ▼                       ▼
Semantic Layer       Query Tool
 │                       │
 └──────────┬────────────┘
            ▼
      Analytics Data
```

The important architectural distinction is:

> **MCP is not the data platform.**

It is an interface through which an AI application can discover and invoke governed capabilities.

The data platform remains responsible for:

* data modeling
* governance
* business definitions
* access control
* quality
* lineage
* analytical correctness

The AI layer consumes those capabilities.

---

### Source generation

```text
src/generator/
```

Synthetic operational data generation.

### CDC infrastructure

```text
infra/cdc/
```

Kafka and Debezium configuration.

### AI layer

```text
ai/
├── semantic_layer.yaml
└── app/
    ├── chatbot.py
    ├── mcp_server.py
    └── web_app.py
```

### Architecture documentation

```text
docs/
```

Detailed architectural reasoning, decisions, repository navigation and future evolution.

---

# Running the Project

## Prerequisites

* Python
* PostgreSQL
* Docker
* Ollama

The AI demonstration uses a local Ollama model, so no paid LLM API is required.

## Start the infrastructure

```powershell
docker compose -f infra/cdc/docker-compose.yml up -d
```

## Start the AI interface

```powershell
python ai/app/web_app.py
```

Open:

```text
http://127.0.0.1:8000
```

Ask a business question.

---

# Example Questions

Try:

```text
What is the total number of payments?
```

```text
Which payment method has the highest number of completed payments?
```

```text
Which customer has the highest completed payment value?
```

The interface exposes both:

1. the generated business answer
2. the SQL used to obtain the answer

This makes the AI behavior inspectable rather than hiding the generated query.

---

# Operational Model vs Analytical Model

The source systems deliberately preserve operational semantics.

For example:

```text
oms.orders
oms.payments
oms.customers
```

are transactional entities.

The analytical layer instead exposes business-oriented concepts such as:

```text
customer_summary
payment_summary
```

This distinction is fundamental to the architecture.

The operational model answers:

> **How does the application store transactions?**

The analytical model answers:

> **How should the business consume information?**

---

# Production Architecture

The local implementation is designed to map onto a production cloud architecture.

| Local / Demonstration     | Production Direction                         |
| ------------------------- | -------------------------------------------- |
| PostgreSQL                | RDS / operational PostgreSQL                 |
| MinIO                     | Amazon S3                                    |
| Local Kafka               | Amazon MSK / managed Kafka                   |
| Local analytical database | Amazon Redshift                              |
| Local orchestration       | Airflow / MWAA                               |
| Local LLM                 | Enterprise-approved hosted/self-hosted model |
| Local MCP server          | Authenticated production service             |
| Local configuration       | Secrets Manager / parameter store            |
| Local monitoring          | CloudWatch + centralized observability       |

The architecture does not fundamentally change.

The infrastructure becomes:

* managed
* highly available
* secured
* observable
* scalable
* recoverable

---

# Engineering Trade-offs

This project deliberately favors architectural clarity over unnecessary infrastructure complexity.

### Why not deploy everything to AWS?

The purpose of the project is to demonstrate **architecture and engineering judgment**, not to create an expensive cloud environment.

Local implementations provide a reproducible development environment while the production architecture documents how those components would evolve.

### Why Kafka?

Because event producers and consumers should not be tightly coupled.

Kafka provides durable event transport and allows multiple downstream consumers.

### Why object storage?

The landing layer creates separation between ingestion and analytical processing.

It also provides a durable historical boundary that downstream systems can consume independently.

### Why a warehouse?

Operational databases should not become the organization's analytical query engine.

### Why a semantic layer?

AI and BI consumers need governed business concepts rather than raw implementation details.

### Why MCP?

MCP provides a standardized interface for AI applications to discover and invoke capabilities.

It does not replace the underlying data governance or analytical architecture.

---

# What This Project Demonstrates

This project is intentionally broader than a traditional ETL exercise.

It demonstrates thinking across:

### Data Engineering

* source systems
* CDC
* event streaming
* ingestion
* landing layers
* warehouse architecture

### Analytics Engineering

* analytical models
* business metrics
* semantic modeling
* governed consumption

### Platform Engineering

* containerized infrastructure
* reproducible local environments
* separation of services
* production evolution

### AI / Data Products

* natural-language analytics
* governed text-to-SQL
* semantic-layer consumption
* MCP tool boundaries

### Architecture

Most importantly, the project demonstrates the ability to reason across the complete path:

> **source → ingestion → storage → transformation → governance → consumption**

rather than treating individual technologies as isolated tools.

---

# Project Evolution

The project was developed incrementally:

```text
Operational Systems
        ↓
Synthetic Data
        ↓
PostgreSQL
        ↓
CDC
        ↓
Kafka
        ↓
Landing Layer
        ↓
Analytics / Warehouse
        ↓
Governed Semantic Layer
        ↓
AI Consumption
        ↓
MCP Extension
```

Each layer was introduced to solve a specific architectural problem.

The project intentionally stops short of implementing every production concern.

The next iteration focuses on productionization rather than adding technologies for their own sake.

---

# Future Evolution

The next production-oriented iteration would introduce:

### Data Platform

* additional source systems
* schema evolution
* incremental ingestion
* replay and recovery
* idempotency
* late-arriving data handling

### Analytics

* dimensional/fact modeling
* dbt
* incremental models
* metric definitions
* lineage

### Reliability

* automated data quality
* freshness monitoring
* pipeline observability
* alerting
* SLA/SLO monitoring

### Platform

* infrastructure as code
* CI/CD
* secrets management
* IAM
* environment separation
* disaster recovery

### AI

* stronger semantic modeling
* query authorization
* query cost controls
* audit logging
* prompt/version management
* text-to-SQL evaluation
* hallucination/error evaluation
* MCP authentication
* multi-tool agents
* controlled write/action capabilities

---

# Interviewer's Guided Tour

If someone asks:

> **"Walk me through the project."**

Use this order:

### 1. Business problem

A multi-regional fulfillment company has multiple operational systems but needs a unified analytical platform.

### 2. Source systems

Start with OMS and explain the operational ownership of customers, orders and payments.

### 3. CDC

Explain why analytics should not continuously query the transactional database.

### 4. Kafka

Explain decoupling and event transport.

### 5. Landing layer

Explain why raw data should have a durable landing boundary.

### 6. Warehouse

Explain why analytical workloads belong downstream of operational systems.

### 7. Analytics models

Open:

```text
analytics.customer_summary
analytics.payment_summary
```

Explain that these are business-facing rather than transactional structures.

### 8. Semantic layer

Open:

```text
ai/semantic_layer.yaml
```

Explain governance and business definitions.

### 9. AI

Open the local chatbot and ask:

> Which payment method has the highest number of completed payments?

Show the generated SQL.

### 10. MCP

Explain that MCP provides a standardized interface for AI applications to interact with governed capabilities.

### 11. Production evolution

Finish with:

> "The local implementation is intentionally lightweight. In production I'd move the landing layer to S3, the warehouse to Redshift, use managed Kafka, add orchestration, observability, IAM, CI/CD and stronger AI governance."

---

# Project Status

**Portfolio status: Working reference implementation**

The repository intentionally distinguishes between:

* **implemented functionality**
* **local simulations**
* **architectural design**
* **production evolution**

No cloud deployment or production-scale claims are implied by the local implementation.

---

## Core Technologies

**Data Engineering**

`PostgreSQL` · `Debezium` · `Apache Kafka` · `S3 / MinIO`

**Analytics**

`SQL` · `Analytics Modeling` · `Semantic Layer`

**AI**

`Ollama` · `LLM-to-SQL` · `MCP`

**Platform**

`Docker` · `Python`

**Production Architecture**

`AWS S3` · `Amazon Redshift` · `MSK` · `Airflow` · `dbt` · `CI/CD` · `Observability`

---

## Author

**ARAF TOA SANJEED KHAN**

Senior Data / Analytics Engineering

Focused on building data platforms that connect **operational systems, analytics, business decision-making and emerging AI capabilities**.
