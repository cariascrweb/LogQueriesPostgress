import os
import time
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "dbname": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
}

TARGET_USR = os.getenv("TARGET_USR", "aurena")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "5"))
LOG_FILE = os.getenv("LOG_FILE", "queries.log")

QUERY_SQL = """
SELECT DISTINCT left(query, 3000) AS query
FROM pg_stat_activity
WHERE usename = %s
  AND state <> 'idle'
  AND query IS NOT NULL
  AND query NOT ILIKE '%%pg_stat_activity%%'
"""

def normalize(q: str) -> str:
    return " ".join(q.split())

def load_seen(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # stored format: [ts] query
            if "] " in line:
                line = line.split("] ", 1)[1]
            seen.add(line)
    return seen

def validate_config():
    missing = [k for k, v in DB_CONFIG.items() if v in (None, "", 0)]
    if missing:
        raise SystemExit(f"Missing .env values: {missing}")

def main():
    validate_config()

    seen = load_seen(LOG_FILE)
    print(f"[INFO] target user={TARGET_USR} interval={POLL_INTERVAL}s loaded_seen={len(seen)} log={LOG_FILE}")

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        while True:
            cur.execute(QUERY_SQL, (TARGET_USR,))
            rows = cur.fetchall()

            new = []
            for (q,) in rows:
                if not q:
                    continue
                qn = normalize(q)
                if qn not in seen:
                    seen.add(qn)
                    new.append(qn)

            if new:
                ts = datetime.utcnow().isoformat() + "Z"
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    for q in new:
                        f.write(f"[{ts}] {q}\n")
                print(f"[+] captured {len(new)} new queries (total_seen={len(seen)})")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n[INFO] stopped")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()