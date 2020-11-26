import logging

from dataclasses import dataclass
from nio import AsyncClient


# The latest migration version of the database.
#
# Database migrations are applied starting from the number specified in the database's
# `migration_version` table + 1 (or from 0 if this table does not yet exist) up until
# the version specified here.
#
# When a migration is performed, the `migration_version` table should be incremented.

latest_migration_version = 0

logger = logging.getLogger(__name__)


@dataclass
class Dbroom:
    room_dbid: str
    room_greeting: str = "Blank?"
    room_rules: str = "Not Implemented Yet."
    is_listed: bool = False


class Storage(object):
    def __init__(self, client: AsyncClient, database_config):
        """Setup the database

        Runs an initial setup or migrations depending on whether a database file has already
        been created

        Args:
            database_config: a dictionary containing the following keys:
                * type: A string, one of "sqlite" or "postgres"
                * connection_string: A string, featuring a connection string that
                    be fed to each respective db library's `connect` method
        """
        self.client = client
        self.conn = self._get_database_connection(
            database_config["type"], database_config["connection_string"]
        )
        self.cursor = self.conn.cursor()
        self.db_type = database_config["type"]

        # Try to check the current migration version
        migration_level = 0
        try:
            self._execute("SELECT version FROM migration_version")
            row = self.cursor.fetchone()
            migration_level = row[0]
        except Exception:
            self._initial_setup()
        finally:
            if migration_level < latest_migration_version:
                self._run_migrations(migration_level)

        logger.info(f"Database initialization of type '{self.db_type}' complete")

    def _get_database_connection(self, database_type: str, connection_string: str):
        if database_type == "sqlite":
            import sqlite3

            # Initialize a connection to the database, with autocommit on
            return sqlite3.connect(connection_string, isolation_level=None)
        elif database_type == "postgres":
            import psycopg2

            conn = psycopg2.connect(connection_string)

            # Autocommit on
            conn.set_isolation_level(0)

            return conn

    def _initial_setup(self):
        """Initial setup of the database"""
        logger.info("Performing initial database setup...")

        # Set up the migration_version table
        self._execute(
            """
            CREATE TABLE migration_version (
                version INTEGER PRIMARY KEY
            )
        """
        )

        # Initially set the migration version to 0
        self._execute(
            """
            INSERT INTO migration_version (
                version
            ) VALUES (%s)
        """,
            (0,),
        )

        # Set up any other necessary database tables here
        self._execute(
            """
            CREATE TABLE room (
            room_dbid TEXT NOT NULL,
            room_greeting TEXT,
            room_rules TEXT,
            is_listed BOOL NOT NULL
            )
            """,
        )

        self._execute(
                """
                alter table only room add constraint rooms_listkey primary key (room_dbid)
                """,
                )

        self._execute(
                """
                create index listed_rooms on room using btree (is_listed)
                """,
                )

        logger.info("Database setup complete")

    def _run_migrations(self, current_migration_version: int):
        """Execute database migrations. Migrates the database to the
        `latest_migration_version`

        Args:
            current_migration_version: The migration version that the database is
                currently at
        """
        logger.debug("Checking for necessary database migrations...")

        if current_migration_version < 1:
            logger.info("Migrating the database from v0 to v1...")

            self._execute("ALTER TABLE room RENAME to room_temp")

            self._execute("drop index listed_rooms")

            self._execute(
                """
                CREATE TABLE room (
                room_dbid TEXT NOT NULL,
                room_greeting TEXT,
                room_rules TEXT,
                is_listed BOOL NOT NULL
                )
                """,
            )

            self.execute(
                    """
                    alter table only room add constraint rooms_listkey primary key (room_dbid)
                    """,
                    )

            self._execute(
                    """
                    create index listed_rooms on room using btree (is_listed)
                    """,
                    )

            self._execute(
                """
                DROP table room_temp
            """
            )
            # Update the stored migration version
            self._execute("UPDATE migration_version SET version = 1")

            logger.info("Database migrated to 1")
        if current_migration_version >= 1:
            new_migration_version = (current_migration_version + 1)

            logger.info(f"Migrating the database from v{current_migration_version} to v{new_migration_version}...")

            self._execute("ALTER TABLE room RENAME to room_temp")

            self._execute("drop index listed_rooms")

            self._execute(
                """
                CREATE TABLE room (
                room_dbid TEXT NOT NULL,
                room_greeting TEXT,
                room_rules TEXT,
                is_listed BOOL NOT NULL
                )
                """,
            )

            self.execute(
                    """
                    alter table only room add constraint rooms_listkey primary key (room_dbid)
                    """,
                    )

            self._execute(
                    """
                    create index listed_rooms on room using btree (is_listed)
                    """,
                    )

            self._execute(
                """
                DROP table room_temp
            """
            )
            # Update the stored migration version
            self._execute("UPDATE migration_version SET version = %s", (new_migration_version))

            logger.info("Database migrated to {new_migration_version}")
            current_migration_version = new_migration_version

    def _execute(self, *args):
        """A wrapper around cursor.execute that transforms placeholder ?'s to %s for postgres
        """
        if self.db_type == "postgres":
            self.cursor.execute(args[0].replace("?", "%s"), *args[1:])
        else:
            self.cursor.execute(*args)

    def load_room_data(self) -> Dbroom:
        self._execute("SELECT * FROM room")
        rows = self.cursor.fetchall()
        dbrooms = {}

        for row in rows:
            room_dbid = row[0]
            room_greeting = row[1]
            room_rules = row[2]
            is_listed = row[3]

            dbrooms[(room_dbid), (room_greeting), (room_rules), (is_listed)] = Dbroom(
                    room_dbid=room_dbid,
                    room_greeting=room_greeting,
                    room_rules=room_rules,
                    is_listed=is_listed
                    )
            return dbrooms

    def store_room_data(self, room: Dbroom):
        self._execute("SELECT * FROM room")
        rows = self.cursor.fetchone()
        for row in rows:
            if row[0] == room.room_dbid:
                self.cursor.execute("DELETE FROM ROW WHERE (room_dbid) = %s", (room.room_id))
        self._execute(
            """
            INSERT INTO room (
                room_dbid,
                room_greeting,
                room_rules,
                is_listed
            ) VALUES (
                %s,%s,%s,%s
            )
        """,
            (
                room.room_dbid,
                room.room_greeting,
                room.room_rules,
                room.is_listed,
            ),
        )

    def delete_room_data(self, room_id: str):
        self.cursor.execute("DELETE FROM room WHERE (room_dbid) = %s", (room_id))
