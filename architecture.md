# Architecture & System Design: Mini Payment-Tracking System

## 1. System Overview
The **Mini Payment-Tracking System** is an asynchronous backend service and Telegram bot designed for educational centers. It tracks enrolled students, logs incoming tuition payments, and calculates monthly outstanding balances (debtors) in real time.

```
                      +-----------------------------+
                      |     Telegram Users / Admins |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Telegram Bot (aiogram 3) |
                      |    - /start, /debt, /pay    |
                      +--------------+--------------+
                                     |
                                     v
+------------------------+    +--------------+--------------+
| Web Clients / Swagger  |--->|    FastAPI Web Service      |
| Endpoint: /api         |    |    - /students CRUD         |
+------------------------+    |    - /payments              |
                              |    - /debtors?month=YYYY-MM |
                              +--------------+--------------+
                                             |
                                             v
                              +-----------------------------+
                              | SQLAlchemy Async Engine     |
                              | SQLite (aiosqlite driver)   |
                              +--------------+--------------+
                                             |
                                             v
                              +-----------------------------+
                              | database:                   |
                              | education_center.db         |
                              +-----------------------------+
```

---

## 2. Component Design

### 2.1 Core Application (`app/`)
- **`app/logger.py`**: Centralized structured logging configuration (`setup_logging`) formatting messages with timestamps, levels, and subsystem names.
- **`app/config.py`**: Settings management using Pydantic Settings reading from `.env`.
- **`app/database.py`**: Async SQLite engine (`sqlite+aiosqlite:///...`), async session factory (`async_sessionmaker`), and declarative Base with connection lifecycle logging.
- **`app/models/`**:
  - `Student`: `id`, `name`, `phone_number`, `group`, `monthly_payment_amount`, `created_at`.
  - `Payment`: `id`, `student_id` (foreign key), `amount`, `date`.
- **`app/seed.py`**: Auto-seeding service populating sample students and payment records on first startup if the database is empty (removable for production).
- **`app/schemas/`**: Pydantic models for validation, request bodies, and response serialization.
- **`app/crud/`**: Pure async database functions for student operations, payment recording, and monthly debtor aggregation with granular execution diagnostics.
- **`app/routers/`**:
  - `/students`: Full CRUD for student records with error handling and request tracking.
  - `/payments`: Register payments and view student payment records.
  - `/debtors`: Query debtors for specified `YYYY-MM`.
- **`app/main.py`**: FastAPI entrypoint with `RequestLoggingMiddleware` (tracking request methods, paths, durations, and HTTP status codes) and Swagger UI exposed at `/api`.

### 2.2 Telegram Bot (`bot/`)
- Built with **`aiogram` 3.x**.
- **`bot/localization.py`**:
  - Centralized dictionary for interface strings.
  - Default language: **Russian** (`ru`).
  - Dynamic user resolution: provides **English** (`en`) for designated reviewer ID (`1124083635`).
- **`bot/handlers/start.py`**: Handles `/start` and `/help`, returning operational instructions.
- **`bot/handlers/debt.py`**: Handles `/debt`, fetching outstanding debtors for the current month and displaying formatted balances.
- **`bot/handlers/pay.py`**: Handles `/pay <student_id> <amount>`, validating numeric arguments, recording the transaction, and returning remaining balance.
- **`bot/main.py`**: Bot startup with Dispatcher and long-polling.

### 2.3 Shared Execution (`run.py`)
- Provides concurrent execution of FastAPI (via `uvicorn`) and the Telegram bot dispatcher within a single async event loop or parallel processes.

---

## 3. Database Schema

### `students`
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `name` (VARCHAR(255), NOT NULL)
- `phone_number` (VARCHAR(32), NOT NULL)
- `group` (VARCHAR(64), NOT NULL)
- `monthly_payment_amount` (FLOAT, NOT NULL)
- `created_at` (DATETIME, NOT NULL, DEFAULT UTC)

### `payments`
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `student_id` (INTEGER, FOREIGN KEY -> `students.id`, NOT NULL)
- `amount` (FLOAT, NOT NULL)
- `date` (DATETIME, NOT NULL, DEFAULT UTC)

---

## 4. Debtor Calculation Logic
For a target month `YYYY-MM`:
1. Find all active students.
2. For each student, sum all `Payment.amount` where `Payment.date` is between the start and end of `YYYY-MM`.
3. Calculate:
   $$\text{debt} = \text{monthly\_payment\_amount} - \text{total\_paid}$$
4. If $\text{debt} > 0$, the student is included in the debtors report with:
   - `student_id`
   - `name`
   - `group`
   - `monthly_payment_amount`
   - `total_paid`
   - `debt`

---

## 5. Architectural Quality Attributes
- **Zero Heavy Dependencies**: Uses SQLite so evaluators do not need Docker or external databases.
- **Asynchronous I/O**: Both API and Bot share asynchronous database sessions via `aiosqlite`.
- **Isolation of Concerns**: Database operations in `crud/`, schemas in `schemas/`, API endpoints in `routers/`, presentation in `handlers/`.
- **Fault-Tolerant Error Handling**: All critical endpoints, database sessions, and bot command handlers employ explicit `try-except` blocks with exception rollbacks and localized fallback responses.
- **Observability & Diagnostics**: Global structured logging with HTTP request middleware measuring latency and database execution tracking across all operational paths.
