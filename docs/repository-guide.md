# Repository Guide

This document explains where to find things in the repository and what each component is responsible for.

Use this as the technical map when navigating or presenting the project.

---

# 1. Repository Structure

```text
multi-source-operational-events/
│
├── README.md
│
├── .env
├── .gitignore
│
├── ai/
│   ├── semantic_layer.yaml
│   └── app/
│       ├── chatbot.py
│       ├── mcp_server.py
│       └── web_app.py
│
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   ├── repository-guide.md
│   └── handbook.md
│
├── infra/
│   └── cdc/
│       ├── docker-compose.yml
│       └── postgres-connector.json
│
└── src/
    └── generator/
        ├── generate.py
        └── generate_wms.py
```

---

# 2. Start Here

If someone opens the repository for the first time:

```text
README.md
    ↓
docs/architecture.md
    ↓
docs/decisions.md
    ↓
docs/repository-guide.md
    ↓
implementation files
```

The README provides the executive overview.

The architecture document explains the system.

The decisions document explains why it was designed that way.

This document explains where the implementation lives.

---

# 3. README.md

### Purpose

The primary portfolio entry point.

It should answer:

* What is this?
* What business problem does it solve?
* What was built?
* What technologies were used?
* What does the architecture look like?
* How do I run it?
* What is implemented versus conceptual?
* Why does this demonstrate senior-level engineering?

For hiring managers and executives, this should be the first and often the only document they need.

---

# 4. `docs/architecture.md`

### Purpose

Detailed architectural explanation.

Use this when discussing:

* Source systems
* CDC
* Kafka
* S3
* Redshift
* Analytical modelling
* Semantic layer
* AI
* MCP
* Agentic investigation
* Local vs production architecture

This answers:

> "How does the whole platform fit together?"

---

# 5. `docs/decisions.md`

### Purpose

Architectural reasoning and trade-offs.

Use this when someone asks:

> "Why did you choose this?"

Examples include:

* Why CDC?
* Why Kafka?
* Why S3?
* Why Redshift?
* Why a semantic layer?
* Why not expose operational tables?
* Why MCP?
* Why not Power Automate?
* Why local LLM?
* Why separate SQL generation from explanation?

This document is particularly useful for senior/lead-level discussions.

---

# 6. `docs/repository-guide.md`

### Purpose

Repository navigation.

This document answers:

> "Where is the thing I want to show?"

Use it during screen sharing.

---

# 7. `docs/handbook.md`

### Purpose

Personal project handbook.

This is the memory scaffold for presenting the project.

It should contain:

* Presentation sequence
* Important files to open
* Key talking points
* Architecture explanations
* Important numbers
* Known limitations
* Interview questions
* Answers / reasoning
* Production evolution

This is deliberately more detailed than the public-facing README.

---

# 8. `ai/`

The AI application layer.

```text
ai/
├── semantic_layer.yaml
└── app/
    ├── chatbot.py
    ├── mcp_server.py
    └── web_app.py
```

---

# 9. `ai/semantic_layer.yaml`

### Purpose

Defines the governed business-facing data interface.

It describes:

* Approved analytical models
* Dimensions
* Metrics
* Business definitions
* Allowed schema
* Forbidden schema

Current governed models include:

```text
customer_summary
payment_summary
```

The semantic layer prevents the AI application from treating the raw operational database as its data interface.

---

# 10. `ai/app/chatbot.py`

### Purpose

Core AI-to-data application.

The current flow is:

```text
User question
     ↓
Local LLM
     ↓
SQL generation
     ↓
SQL validation
     ↓
Analytics schema
     ↓
PostgreSQL
     ↓
Query result
     ↓
Local LLM
     ↓
Business answer
```

Important responsibilities:

### `load_semantic_layer()`

Loads the governed semantic definition.

### `build_system_prompt()`

Provides the model with the available governed data structures and SQL rules.

### `generate_sql()`

Asks the local LLM to translate a business question into SQL.

### `validate_sql()`

Acts as the application-level safety boundary before database execution.

### `execute_sql()`

Executes validated SQL.

### `explain_result()`

Converts query results into a concise business explanation.

### `main()`

Runs the command-line chatbot loop.

---

# 11. `ai/app/web_app.py`

### Purpose

Web interface for the AI assistant.

It exposes the chatbot functionality through a browser rather than the command line.

Conceptually:

```text
Browser
   ↓
Web application
   ↓
Chatbot logic
   ↓
Local LLM
   ↓
Governed analytics
   ↓
PostgreSQL
```

This is the easiest component to demonstrate visually.

---

# 12. `ai/app/mcp_server.py`

### Purpose

MCP interface for exposing governed capabilities to AI applications.

The MCP server sits between an AI client and approved data capabilities.

Conceptually:

```text
AI Client
    ↓
MCP
    ↓
Governed tools
    ↓
Analytics layer
```

It is intentionally separate from the chatbot.

The chatbot demonstrates direct application-level AI integration.

The MCP server demonstrates how the same governed capabilities can be exposed through a standardized AI tool interface.

---

# 13. `infra/cdc/`

CDC infrastructure.

```text
infra/cdc/
├── docker-compose.yml
└── postgres-connector.json
```

---

# 14. `infra/cdc/docker-compose.yml`

Defines the local Kafka and Debezium infrastructure.

Services:

```text
Kafka
Debezium Connect
```

Kafka provides event streaming.

Debezium Connect captures database changes and publishes them into Kafka.

---

# 15. `infra/cdc/postgres-connector.json`

Defines the Debezium PostgreSQL source connector.

Important configuration includes:

* PostgreSQL connection
* Database name
* Schema selection
* Replication plugin
* Publication
* Kafka topic prefix

The connector captures changes from:

```text
oms
```

---

# 16. `src/generator/`

Synthetic source-data generation.

```text
src/generator/
├── generate.py
└── generate_wms.py
```

The project uses synthetic data so that the entire platform can be reproduced without proprietary enterprise data.

---

# 17. `src/generator/generate.py`

Generates OMS data.

Current entities:

```text
customers
orders
payments
```

Current scale:

```text
10,000 customers
100,000 orders
100,000 payments
```

The generator uses deterministic random seeds so that the dataset can be reproduced.

---

# 18. `src/generator/generate_wms.py`

Generates WMS data.

Current entities:

```text
warehouses
inventory
fulfillment_events
```

Current target scale:

```text
50 warehouses
100,000 inventory records
500,000 fulfillment events
```

This demonstrates a second operational source with a different database technology.

---

# 19. `.env`

Contains local configuration such as database connection information.

This file should never contain production credentials in a public repository.

`.gitignore` should prevent sensitive local configuration from being committed.

---

# 20. What to Open During a Technical Walkthrough

A useful presentation sequence is:

### 1. README

Start with the business problem and architecture.

### 2. `docs/architecture.md`

Show the complete platform.

### 3. `src/generator/generate.py`

Show how synthetic operational data is created.

### 4. PostgreSQL

Show:

```text
oms.customers
oms.orders
oms.payments
```

### 5. CDC configuration

Open:

```text
infra/cdc/postgres-connector.json
```

Explain:

```text
PostgreSQL
    ↓
Debezium
    ↓
Kafka
```

### 6. Analytical layer

Show:

```text
analytics.customer_summary
analytics.payment_summary
```

Explain why consumers do not query `oms` directly.

### 7. Semantic layer

Open:

```text
ai/semantic_layer.yaml
```

Explain the governed interface.

### 8. AI application

Open:

```text
ai/app/chatbot.py
```

Show:

```text
Question
→ LLM
→ SQL
→ validation
→ analytics
→ result
→ explanation
```

### 9. Web application

Open the local web interface and ask a business question.

### 10. MCP

Open:

```text
ai/app/mcp_server.py
```

Explain where MCP fits and why it is separate from the underlying data platform.

### 11. Production architecture

Return to the README/architecture document and explain:

```text
Local
→
AWS production equivalent
```

---

# 21. Fast Navigation by Question

### "Where is the business context?"

```text
README.md
```

### "Where is the architecture?"

```text
docs/architecture.md
```

### "Why did you choose this architecture?"

```text
docs/decisions.md
```

### "Where is the data generation?"

```text
src/generator/
```

### "Where is CDC configured?"

```text
infra/cdc/
```

### "Where is AI governance defined?"

```text
ai/semantic_layer.yaml
```

### "Where is SQL generated?"

```text
ai/app/chatbot.py
```

### "Where is the web UI?"

```text
ai/app/web_app.py
```

### "Where is MCP?"

```text
ai/app/mcp_server.py
```

### "Where are your personal presentation notes?"

```text
docs/handbook.md
```

---

# 22. Implementation Boundary

The repository intentionally contains both implementation and architectural representation.

When presenting the project, always distinguish:

```text
IMPLEMENTED
```

from:

```text
ARCHITECTURALLY DESIGNED
```

and:

```text
PRODUCTION NEXT
```

Do not represent a production AWS component as deployed when it was only designed.

That distinction is part of the project's engineering credibility.
