# Armenian Wildberries Local Seller & Buyer Telegram Bot

An asynchronous Telegram bot built with **Python 3.11+**, **aiogram 3.x**, **PostgreSQL (SQLAlchemy async + Alembic)**, **Redis**, and **ARQ** for connecting local Armenian Wildberries sellers with buyers for fast local delivery (1-2 days).

## Features

- **Multi-language Support (i18n)**: Armenian (default, `hy`), Russian (`ru`), and English (`en`).
- **Buyer Functionality**:
  - Main welcome menu & language switcher.
  - Category navigation for items stored in Armenian local stock.
  - Fast search & bargain deals section sorted by highest discounts.
  - Interactive product cards displaying images, prices, discounts, delivery times, and direct Wildberries app deeplinks.
- **Seller Functionality**:
  - WB Supplier API Key onboarding and encryption (Fernet symmetric encryption).
  - WB product stock & catalog synchronization.
  - Seller dashboard to toggle products flagged as local Armenian stock.
  - Manual & scheduled hourly stock sync via ARQ background worker.
- **Robust Tech Stack & Architecture**:
  - Clean modular architecture (`core/`, `models/`, `services/`, `handlers/`).
  - Containerization with Docker Compose (Bot, ARQ Worker, PostgreSQL, Redis).
  - Automated database migrations using Alembic.
  - Comprehensive unit & integration tests with `pytest` and `pytest-asyncio`.

## Project Structure

```
.
├── alembic/                # Database migration scripts
├── core/                   # App configurations, security, DB engine & i18n
│   ├── config.py
│   ├── database.py
│   ├── i18n.py
│   └── security.py
├── models/                 # SQLAlchemy Async Models (User, Seller, Product)
│   ├── user.py
│   ├── seller.py
│   └── product.py
├── services/               # WB API client, DB product services, ARQ worker
│   ├── wb_api.py
│   ├── product_service.py
│   └── arq_worker.py
├── handlers/               # Aiogram Telegram bot UI handlers
│   ├── common.py
│   ├── buyer.py
│   └── seller.py
├── tests/                  # Pytest test suite
│   ├── test_wb_api.py
│   └── test_database.py
├── main.py                 # Bot entrypoint
├── pyproject.toml          # Project dependencies & package config
├── docker-compose.yml      # Docker service orchestration
└── .env.example            # Environment variable template
```

## Setup & Running

### Using Docker Compose (Recommended)

1. Copy `.env.example` to `.env` and fill in your Telegram Bot Token and parameters:
   ```bash
   cp .env.example .env
   ```
2. Start the services using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

### Running Tests Locally

```bash
pip install pytest pytest-asyncio pytest-mock aiosqlite cryptography httpx sqlalchemy redis arq pydantic-settings aiogram alembic asyncpg
pytest
```
