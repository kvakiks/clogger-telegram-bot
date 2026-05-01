# CashLogger — your digital financial diary

A Telegram bot for expense tracking: choose currency, log expenses by category, view period reports, and use admin tools.

## Features

- Currency selection on first launch (`RUB`, `ILS`, `EUR`, `USD`, `KZT`, `GEL`).
- Add expenses in format: `<category> <amount>`.
- View the list of available categories.
- Inline reports for periods: day, week, 2 weeks, month, quarter.
- Admin panel: total users and user list.
- FSM state recovery so users continue where they left off.

## Stack

- Python 3.14+
- aiogram 3.x
- SQLAlchemy 2.x (async)
- PostgreSQL (`asyncpg`)

## Bot Structure

- `app.py` — entry point, bot startup, and middleware registration.
- `handlers/user.py` — user and admin handlers.
- `keyboards/` — inline keyboards.
- `database/models.py` — DB models.
- `database/engine.py` — DB connection and session maker.
- `database/requests.py` — DB query functions.
- `middlewares/db.py` — middleware that injects `AsyncSession` into handlers.

## Installation

1. Clone the repository:
   `git clone <repo_url>`
2. Go to the project folder:
   `cd ML`
3. Create and activate a virtual environment:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
4. Install dependencies:
   `pip install -r requirements.txt`

## Environment Setup

Create a `.env` file in the project root:

`TOKEN=your_bot_token`
`DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname`
`ADMIN_IDS=123456789,987654321`

## Run

- Start the bot:
  `python app.py`

Database tables are created automatically on startup.

## Usage

- `/start` — start or return to the working state.
- `/admin` — admin panel (only for IDs in `ADMIN_IDS`).
- Expense format example: `food 470`.

## Improvement Ideas

- Top spending categories output.
- Deleting user & user's history if he wants.
