
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "scoutlocal.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scouting_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,

                player_name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                position TEXT NOT NULL,

                scout_name TEXT NOT NULL DEFAULT '',

                observation_date TEXT NOT NULL,
                match_context TEXT NOT NULL DEFAULT '',

                technical_rating INTEGER,
                tactical_rating INTEGER,
                physical_rating INTEGER,

                strengths TEXT NOT NULL DEFAULT '',
                weaknesses TEXT NOT NULL DEFAULT '',
                observations TEXT NOT NULL DEFAULT '',

                recommendation TEXT NOT NULL DEFAULT 'Monitor',

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                CHECK (
                    technical_rating BETWEEN 1 AND 5
                    OR technical_rating IS NULL
                ),

                CHECK (
                    tactical_rating BETWEEN 1 AND 5
                    OR tactical_rating IS NULL
                ),

                CHECK (
                    physical_rating BETWEEN 1 AND 5
                    OR physical_rating IS NULL
                )
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_scouting_reports_player
            ON scouting_reports (player_id, team_id)
            """
        )


def save_scouting_report(report):
    initialize_database()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    fields = (
        "player_id",
        "team_id",
        "player_name",
        "team_name",
        "position",
        "scout_name",
        "observation_date",
        "match_context",
        "technical_rating",
        "tactical_rating",
        "physical_rating",
        "strengths",
        "weaknesses",
        "observations",
        "recommendation",
    )

    values = [report[field] for field in fields]

    placeholders = ", ".join(
        "?" for _ in fields
    )

    columns = ", ".join(fields)

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            INSERT INTO scouting_reports (
                {columns}, created_at, updated_at
            )
            VALUES (
                {placeholders}, ?, ?
            )
            """,
            values + [timestamp, timestamp],
        )

        return cursor.lastrowid


def get_player_reports(player_id, team_id):
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM scouting_reports
            WHERE player_id = ? AND team_id = ?
            ORDER BY observation_date DESC, id DESC
            """,
            (int(player_id), int(team_id)),
        ).fetchall()

    return [dict(row) for row in rows]


def get_all_reports():
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM scouting_reports
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def update_scouting_report(report_id, updates):
    initialize_database()

    editable_fields = {
        "scout_name",
        "observation_date",
        "match_context",
        "technical_rating",
        "tactical_rating",
        "physical_rating",
        "strengths",
        "weaknesses",
        "observations",
        "recommendation",
    }

    invalid = set(updates) - editable_fields

    if invalid:
        raise ValueError(
            f"Fields cannot be updated: {sorted(invalid)}"
        )

    if not updates:
        return False

    assignments = ", ".join(
        f"{field} = ?"
        for field in updates
    )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    values = list(updates.values()) + [
        timestamp,
        int(report_id),
    ]

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            UPDATE scouting_reports
            SET {assignments}, updated_at = ?
            WHERE id = ?
            """,
            values,
        )

        return cursor.rowcount > 0


def delete_scouting_report(report_id):
    initialize_database()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM scouting_reports
            WHERE id = ?
            """,
            (int(report_id),),
        )

        return cursor.rowcount > 0
