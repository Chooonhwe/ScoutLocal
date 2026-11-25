
from datetime import datetime, timezone

from scoutlocal.database.scouting_db import get_connection


RECRUITMENT_STATUSES = [
    "Identified",
    "Under Review",
    "Shortlisted",
    "Recommended",
    "Archived",
]

RECRUITMENT_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical",
]


def current_timestamp():
    return datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )


def initialize_recruitment_database():
    """
    Create the recruitment table if it does not exist.
    Existing scouting reports are not modified.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS recruitment_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,

                player_name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                position TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'Identified',
                priority TEXT NOT NULL DEFAULT 'Medium',
                notes TEXT NOT NULL DEFAULT '',

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE(player_id, team_id),

                CHECK (
                    status IN (
                        'Identified',
                        'Under Review',
                        'Shortlisted',
                        'Recommended',
                        'Archived'
                    )
                ),

                CHECK (
                    priority IN (
                        'Low',
                        'Medium',
                        'High',
                        'Critical'
                    )
                )
            )
            """
        )


def add_recruitment_target(player, priority="Medium", notes=""):
    """
    Add a player to the recruitment database.

    Returns True if newly added.
    Returns False if the player already exists.
    """
    if priority not in RECRUITMENT_PRIORITIES:
        raise ValueError("Invalid recruitment priority.")

    initialize_recruitment_database()

    timestamp = current_timestamp()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO recruitment_targets (
                player_id,
                team_id,
                player_name,
                team_name,
                position,
                status,
                priority,
                notes,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(player["player_id"]),
                int(player["team_id"]),
                str(player["player_name"]),
                str(player["team_name"]),
                str(player["primary_position_group"]),
                "Identified",
                priority,
                notes,
                timestamp,
                timestamp,
            ),
        )

        return cursor.rowcount > 0


def get_recruitment_targets():
    """Retrieve all recruitment targets."""
    initialize_recruitment_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM recruitment_targets
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_player_recruitment_target(player_id, team_id):
    """Retrieve one player's recruitment record."""
    initialize_recruitment_database()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM recruitment_targets
            WHERE player_id = ? AND team_id = ?
            """,
            (int(player_id), int(team_id)),
        ).fetchone()

    return dict(row) if row else None


def update_recruitment_target(
    target_id,
    status,
    priority,
    notes,
):
    """Update the recruitment status, priority and notes."""
    if status not in RECRUITMENT_STATUSES:
        raise ValueError("Invalid recruitment status.")

    if priority not in RECRUITMENT_PRIORITIES:
        raise ValueError("Invalid recruitment priority.")

    initialize_recruitment_database()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE recruitment_targets
            SET status = ?,
                priority = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                priority,
                notes,
                current_timestamp(),
                int(target_id),
            ),
        )

        return cursor.rowcount > 0


def remove_recruitment_target(target_id):
    """Remove a player from the recruitment database."""
    initialize_recruitment_database()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM recruitment_targets
            WHERE id = ?
            """,
            (int(target_id),),
        )

        return cursor.rowcount > 0
