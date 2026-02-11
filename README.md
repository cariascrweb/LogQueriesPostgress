# PostgreSQL Query Collector (pg-query-collector)

## 📌 Purpose

This project runs a **background service** on an Ubuntu server that continuously
monitors **live PostgreSQL queries** executed by a specific database user and
stores **only distinct SQL queries** in a log file.

It is designed for environments where:

- PostgreSQL **cannot be restarted**
- `pg_stat_statements` **cannot be enabled**
- Only **read access** to PostgreSQL is available

The service runs **24/7**, survives reboots, and does not require an open terminal.

---

## 🧠 How it works (high level)

- Connects to PostgreSQL using credentials from `.env`
- Polls `pg_stat_activity` every _N seconds_
- Extracts only the `query` column
- Stores **distinct queries only**
- Writes results to `queries.log`
- Runs as a **systemd service**

⚠️ Limitation:
Only queries that are **running at the moment of polling** can be captured.
Very fast queries may be missed.

---

## 📁 Project structure

```text
LogQueriesPostgress/
├── collector.py        # Main Python script
├── requirements.txt    # Python dependencies
├── .env                # DB credentials & config (restricted permissions)
├── queries.log         # Distinct captured SQL queries
├── service.log         # Optional service output (if enabled)
└── venv/               # Python virtual environment
```
