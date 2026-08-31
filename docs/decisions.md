# Engineering Decisions & Trade-offs

This document records the major architectural decisions behind the platform and the reasoning behind them.

The goal is not to present one "perfect" architecture, but to show how the design responds to business requirements, scale, governance, and operational constraints.

---

## 1. Preserve Operational Source Semantics

### Decision

Keep the source-system model separate from the analytical model.

### Why

Operational systems are designed around application transactions, not analytical consumption.

Directly exposing:

```text
oms.customers
oms.orders
oms.payments
```

to every downstream consumer would force each consumer to understand operational relationships and business rules independently.

Instead:

```text
Operational Model
       ↓
Transformation
       ↓
Analytical Model
       ↓
Consumers
```

This creates a stable boundary between operational systems and downstream analytics.

---

## 2. Do Not Force Everything Through Streaming

### Decision

Use streaming selectively and retain batch processing for workloads that do not require low latency.

### Why

Streaming introduces operational complexity:

* Infrastructure
* Monitoring
* Failure handling
* Ordering concerns
* Replay management
* Consumer management

Not every dataset benefits from that complexity.

Operational events where freshness matters can use CDC/Kafka.

Reference and historical data can use batch ingestion.

### Trade-off

A hybrid architecture is more complex than a single ingestion pattern, but avoids paying streaming complexity where it provides little business value.

---

## 3. Use CDC for Operational Changes

### Decision

Use Debezium and Kafka to capture database changes.

### Why

Polling source databases repeatedly is inefficient and can introduce:

* Duplicate processing
* Missed updates
* Increased source-system load
* Latency

CDC captures changes from the database transaction log and provides an event-driven ingestion mechanism.

### Trade-off

CDC introduces additional infrastructure and operational requirements.

For high-value operational events, the lower latency and change fidelity justify the complexity.

---

## 4. Use S3 as the Durable Landing Layer

### Decision

Use object storage as the durable landing boundary before analytical processing.

### Why

A durable landing layer provides:

* Raw-data retention
* Replay capability
* Decoupling from downstream systems
* Historical recovery
* Independent reprocessing

This also prevents the warehouse from becoming the only copy of incoming data.

### Production choice

Amazon S3 is the intended production implementation.

The local project does not require an AWS account, so the architecture is demonstrated rather than deployed.

---

## 5. Use Redshift for Analytical Consumption

### Decision

Use Amazon Redshift as the production analytical warehouse.

### Why

The target workloads include:

* Aggregation
* KPI reporting
* Cross-domain analysis
* BI workloads
* AI-assisted analytical queries

These workloads are fundamentally different from transactional application workloads.

### Boundary

```text
Operational databases
        ≠
Analytical warehouse
```

This separation allows each system to be optimized for its intended workload.

---

## 6. Build Analytical Models Before AI Consumption

### Decision

AI should consume governed analytical models rather than raw operational tables.

### Why

An LLM can generate syntactically valid SQL that is still:

* Semantically wrong
* Based on the wrong table
* Based on duplicated data
* Based on an incorrect business definition

For example:

```text
"Revenue"
```

may have different definitions across departments.

The analytical layer establishes the business logic before AI is allowed to consume it.

---

## 7. Introduce a Governed Semantic Layer

### Decision

Create an explicit semantic layer defining approved models, dimensions, and metrics.

### Why

The semantic layer acts as a contract between the data platform and downstream consumers.

It tells consumers:

* What data exists
* What it means
* What can be queried
* Which metrics are approved
* Which schemas are off limits

This is especially important for AI because language models can generate queries that are technically valid but business-invalid.

---

## 8. Validate AI-Generated SQL

### Decision

Never execute model-generated SQL blindly.

The local implementation validates generated SQL before execution.

### Current controls

The validator checks that:

```text
SELECT / WITH only
        +
analytics schema required
        +
write operations rejected
```

### Why

The LLM is probabilistic.

The database execution boundary should not be.

The model generates a proposal.

The application validates that proposal.

Only then does the database execute it.

---

## 9. Separate SQL Generation from Result Explanation

### Decision

Use two logical AI steps:

```text
Business question
       ↓
SQL generation
       ↓
Database
       ↓
Result
       ↓
Business explanation
```

### Why

SQL generation and business explanation are different responsibilities.

The first needs to produce executable SQL.

The second needs to communicate the result clearly.

Separating them makes failures easier to diagnose and reduces the chance that the explanation step invents data.

---

## 10. MCP Is an Interface, Not the Data Platform

### Decision

Treat MCP as an integration/tool interface above governed data capabilities.

### Why

MCP does not replace:

* Data modelling
* Warehousing
* Governance
* Semantic modelling
* Security
* Business logic

Instead, it standardizes how AI applications can discover and invoke capabilities.

Conceptually:

```text
AI Application
      ↓
     MCP
      ↓
Governed Tools
      ↓
Semantic / Analytical Layer
      ↓
Warehouse
```

The underlying data architecture remains important regardless of whether MCP is used.

---

## 11. Simple Chatbot vs Agentic AI

### Decision

Do not introduce agentic behavior unless the use case actually requires multiple reasoning or tool steps.

### Simple question

```text
"What is the total number of payments?"
```

can use:

```text
Question
   ↓
SQL
   ↓
Result
```

### Complex investigation

```text
"Why has our most important customer started ordering less?"
```

may require:

```text
Find customer
      ↓
Retrieve customer metrics
      ↓
Analyze trend
      ↓
Check payment behavior
      ↓
Check fulfillment behavior
      ↓
Compare against peers
      ↓
Synthesize evidence
```

The second problem benefits from tool orchestration and potentially agentic behavior.

### Principle

**Use an agent because the workflow requires one, not because "agentic AI" is fashionable.**

---

## 12. Why the Local LLM Is Useful

### Decision

Use Ollama with a local model for the portfolio implementation.

### Why

The project does not require:

* Paid API access
* Cloud model credentials
* External inference infrastructure

The local model is sufficient to demonstrate the architecture:

```text
User
 ↓
LLM
 ↓
Governed SQL
 ↓
Database
 ↓
LLM
 ↓
Answer
```

### Limitation

A small local model is less capable than production-grade hosted models.

The architecture therefore matters more than model performance in this project.

---

## 13. Why PostgreSQL Is Used Locally

### Decision

Use PostgreSQL as the local development and analytical environment.

### Why

It provides:

* Easy local setup
* SQL compatibility
* Low cost
* Reproducibility
* Easy demonstration

The production architecture can move the analytical workload to Redshift without changing the conceptual downstream interface.

---

## 14. Why Not Connect AI Directly to OMS?

### Decision

Do not allow the AI layer to directly query:

```text
oms.*
```

### Why

This would create coupling between AI and operational systems.

It could also expose:

* Internal implementation details
* Sensitive operational structures
* Inconsistent business logic
* Unnecessary tables
* Transactional workloads

Instead:

```text
OMS
 ↓
Analytical transformation
 ↓
Governed analytics
 ↓
AI
```

---

## 15. Why Not Use Power Automate / Zapier for Everything?

Automation platforms are excellent when the workflow is deterministic.

For example:

```text
New payment
 ↓
Send notification
 ↓
Create task
```

An AI/agent architecture becomes more useful when the workflow requires interpretation, investigation, or dynamic tool selection.

For example:

```text
Customer revenue dropped
 ↓
Identify affected customer
 ↓
Determine when decline started
 ↓
Compare historical behavior
 ↓
Check payment failures
 ↓
Check fulfillment issues
 ↓
Investigate regional patterns
 ↓
Produce explanation
```

The distinction is therefore:

```text
Deterministic workflow
→ Automation platform

Analytical investigation
→ AI + governed tools
```

There can also be a hybrid architecture where AI determines what needs to happen and deterministic automation executes the approved action.

---

## 16. Why Not Build Everything in Python?

Python remains useful for:

* Data generation
* Transformation
* APIs
* Application logic
* Orchestration
* Custom tooling

But Python itself does not provide the architectural boundaries required by an enterprise data platform.

The project therefore demonstrates technologies according to their responsibilities rather than treating one language or tool as the entire platform.

---

## 17. Local vs Production Trade-off

The project deliberately separates architectural intent from implementation cost.

### Local implementation

Optimized for:

* Reproducibility
* Learning
* Demonstration
* Portfolio accessibility
* Zero cloud cost

### Production architecture

Optimized for:

* Scale
* Reliability
* Security
* Governance
* Observability
* Availability
* Operational ownership

This means some production components are represented architecturally rather than deployed.

That is intentional rather than accidental.

---

## 18. Core Design Principle

The platform follows one central principle:

> **Consumers should interact with governed business data, not raw operational infrastructure.**

The layers therefore evolve as:

```text
Operational Systems
        ↓
Ingestion
        ↓
Durable Landing
        ↓
Analytical Warehouse
        ↓
Transformation
        ↓
Governed Semantic Layer
        ↓
BI / AI / Applications
```

Each layer has a clear responsibility.

That separation is what makes the platform extensible from traditional analytics into AI-assisted and agentic use cases.
