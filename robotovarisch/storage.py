import logging

from dataclasses import dataclass
from nio import AsyncClient
from robotovarisch.chat_functions import send_text_to_room


latest_migration_version = 0

logger = logging.getLogger(__name__)


@dataclass
class Dbroom:
    room_dbid: str
    room_greeting: str
    room_rules: str
    is_listed: bool


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
            room_dbid TEXT PRIMARY KEY,
            room_greeting TEXT,
            room_rules TEXT,
            is_listed BOOL NOT NULL
            )
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
                room_dbid TEXT PRIMARY KEY,
                room_greeting TEXT,
                room_rules TEXT,
                is_listed BOOL NOT NULL
                )
                """,
            )

            self._execute(
                """
                INSERT INTO room (
                    room_dbid,
                    room_greeting,
                    room_rules,
                    is_listed
                )
                SELECT FROM room_temp (
                    room_dbid,
                    room_greeting,
                    room_rules,
                    is_listed
                )
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
                room_dbid TEXT PRIMARY KEY,
                room_greeting TEXT,
                room_rules TEXT,
                is_listed BOOL NOT NULL
                )
                """,
            )

            self._execute(
                """
                INSERT INTO room (
                    room_dbid,
                    room_greeting,
                    room_rules,
                    is_listed
                )
                SELECT FROM room_temp (
                    room_dbid,
                    room_greeting,
                    room_rules,
                    is_listed
                )
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

    async def load_room_greeting(self, curr_room: str):
        try:
            text = self._execute("SELECT room_greeting FROM room WHERE room_dbid = %s", (curr_room))
            await send_text_to_room(self.client, curr_room, text)
        except Exception:
            logger.info("no greetng")

    def load_room_rules(self, curr_room: str):
        try:
            text = self._execute("SELECT room_rules FROM room WHERE room_dbid = %s", (curr_room))
            await send_text_to_room(self.client, curr_room, text)
        except Exception:
            logger.info("no rules just right")

    def store_room_rules(self, room_rules: str):
        try:
            self._execute("UPDATE room SET room_rules = %s", (room_rules))
        except Exception:
            logger.info(f"adding room_rules for {self.room.room_id}")
            self._execute(
               """
               INSERT INTO room (
                   room_dbid,
                   room_rules,
               ) VALUES (
                   %s,%s
               )
           """,
               (
                   self.room.room_id,
                   room_rules,
               ),
               )

    def store_room_greeting(self, room_greeting: str):
        try:
            self._execute("UPDATE room SET room_greeting = %s", (room_greeting))
            logger.info("successfuly chanfed grrrtz")
        except Exception:
            logger.info(f"adding room_greeting for {self.room.room_id}")
        self._execute(
              """
              INSERT INTO room (
                  room_dbid,
                  room_greeting
              ) VALUES (
                  %s,%s
              )
          """,
              (
                  self.room.room_id,
                  room_greeting,
              ),
          )

    def toggle_room_public(self):
        try:
            self._execute("UPDATE room SET is_listed = NOT is_listed WHERE room_dbid = %s", (self.room.room_id))
        except Exception:
            text = "please set a room greeting or rules first"
            self.send_to_room(self.client, self.room.room_id, text)

    def delete_room_data(self, curr_room: str):
        self.cursor.execute("DELETE FROM room WHERE (room_dbid) = %s", (curr_room))
