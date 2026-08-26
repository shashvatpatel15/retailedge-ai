import sqlite3

from app.core.config import LOCAL_DB_PATH


def get_connection():
    LOCAL_DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        LOCAL_DB_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_local_db():
    connection = get_connection()

    try:
        connection.execute(
            "PRAGMA journal_mode=WAL;"
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS queue_outbox (

                event_id TEXT PRIMARY KEY,

                device_id TEXT NOT NULL,

                recorded_at TEXT NOT NULL,

                tracked_people INTEGER NOT NULL DEFAULT 0,

                queue_length INTEGER NOT NULL DEFAULT 0,

                average_wait REAL NOT NULL DEFAULT 0,

                longest_wait REAL NOT NULL DEFAULT 0,

                alert INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_queue_outbox_created_at
            ON queue_outbox(created_at);
            """
        )

        connection.commit()

        print(
            "Local SQLite database ready:",
            LOCAL_DB_PATH
        )

    finally:
        connection.close()


def save_pending_metric(payload):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO queue_outbox (
                event_id,
                device_id,
                recorded_at,
                tracked_people,
                queue_length,
                average_wait,
                longest_wait,
                alert
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                payload["event_id"],
                payload["device_id"],
                payload["recorded_at"],
                payload["tracked_people"],
                payload["queue_length"],
                payload["average_wait"],
                payload["longest_wait"],
                1 if payload["alert"] else 0
            )
        )

        connection.commit()

    finally:
        connection.close()


def get_pending_metrics(limit=20):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                event_id,
                device_id,
                recorded_at,
                tracked_people,
                queue_length,
                average_wait,
                longest_wait,
                alert
            FROM queue_outbox
            ORDER BY created_at ASC
            LIMIT ?;
            """,
            (limit,)
        ).fetchall()

        return [
            {
                "event_id": row["event_id"],
                "device_id": row["device_id"],
                "recorded_at": row["recorded_at"],
                "tracked_people": row["tracked_people"],
                "queue_length": row["queue_length"],
                "average_wait": row["average_wait"],
                "longest_wait": row["longest_wait"],
                "alert": bool(row["alert"]),
            }
            for row in rows
        ]

    finally:
        connection.close()


def delete_pending_metric(event_id):
    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM queue_outbox
            WHERE event_id = ?;
            """,
            (event_id,)
        )

        connection.commit()

    finally:
        connection.close()


def get_pending_count():
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM queue_outbox;
            """
        ).fetchone()

        return row["total"]

    finally:
        connection.close()