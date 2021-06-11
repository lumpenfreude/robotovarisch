import logging

from nio import AsyncClient, MatrixRoom
from psycopg2 import sql

latest_migration_version = 0

logger = logging.getLogger(__name__)


class Storage(object):
    def __init__(self, client: AsyncClient, room: MatrixRoom, database_config):
        self.client = client
        self.conn = self._get_database_connection(
            database_config["type"], database_config["connection_string"]
        )
        self.cursor = self.conn.cursor()
        self.db_type = database_config["type"]
        self.room = room
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
            room_dbname TEXT,
            room_greeting TEXT,
            room_rules TEXT,
            greeting_enabled BOOL
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
                room_dbname TEXT,
                room_greeting TEXT,
                room_rules TEXT,
                greeting_enabled BOOL
                )
                """,
            )

            self._execute(
                """
                INSERT INTO room (
                    room_dbid,
                    room_dbname,
                    room_greeting,
                    room_rules,
                    greeting_enabled
                )
                SELECT FROM room_temp (
                    room_dbid,
                    room_dbname,
                    room_greeting,
                    room_rules,
                    greeting_enabled
                )
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

            self._execute(
                """
                CREATE TABLE room (
                room_dbid TEXT PRIMARY KEY,
                room_dbname TEXT,
                room_greeting TEXT,
                room_rules TEXT,
                greeting_enabled BOOL
                )
                """,
            )

            self._execute(
                """
                INSERT INTO room (
                    room_dbid,
                    room_dbname,
                    room_greeting,
                    room_rules,
                    greeting_enabled
                )
                SELECT FROM room_temp (
                    room_dbid,
                    room_dbname,
                    room_greeting,
                    room_rules,
                    greeting_enabled
                )
                """,
            )

            self._execute(
                """
                DROP table room_temp
                """
                )
            # Update the stored migration version
            self.cursor.execute("UPDATE migration_version SET version = %s", (new_migration_version))

            logger.info("Database migrated to {new_migration_version}")
            current_migration_version = new_migration_version

    def _execute(self, *args):
        """A wrapper around cursor.execute that transforms placeholder ?'s to %s for postgres
        """
        if self.db_type == "postgres":
            self.cursor.execute(args[0].replace("?", "%s"), *args[1:])
        else:
            self.cursor.execute(*args)

    def on_room_join(self):
        sqlreq = "INSERT INTO ROOM (room_dbid, room_dbname, room_rules, greeting_enabled) VALUES (%s, %s, %s, %s);"
        default_greeting = "Hello I am a robot. Please set me up."
        default_rules = "No rules set. Follow the server rules ***or else.***"
        greet_default = FALSE
        self.cursor.execute(sqlreq, (self.room.room_id, self.room.display_name, default_greeting, default_rules, greet_default)

    def load_room_data(self, record):
        sqlreq = """
                SELECT {field} FROM room WHERE room_dbid = {working_room};
                """
        self.cursor.execute(sqlreq)
        record = self.cursor.fetchall()
        thing = type(record)
        logger.info(f"record is {thing}")
        return record 

    def save_room_data(self):
        sqlreq = """
                UPDATE room
                SET {field} = {info}
                WHERE room_dbid = {self.room.room_id};
                """
        self.cursor.execute(sqlreq)

    def toggle_room_setting(self):
        sqlreq = """
                UPDATE table SET boolean_field = NOT boolean_field WHERE id = {field};
                """
        self.cursor.execute(sqlreq)
