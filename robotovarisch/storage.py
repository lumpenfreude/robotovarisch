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

    def load_room_data(self, curr_room, info):
        if info == "room_greeting":
            query = sql.SQL("select {field} from {table} where {pkey} = %s").format(
                field=sql.Identifier('room_greeting'),
                table=sql.Identifier('room'),
                pkey=sql.Identifier('room_dbid')
                )
            self.cursor.execute(query, (curr_room,))
            record = self.cursor.fetchall()
            self.conn.commit()
            if record is not None:
                greetings = record[0]
                greeting = greetings[0]
            else:
                greeting = "no greeting set PLEWSE LET ME GREET TYEBPEOLEPELE"
            return greeting
        elif info == "room_rules":
            query = sql.SQL("select {field} from {table} where {pkey} = %s").format(
                field=sql.Identifier('room_rules'),
                table=sql.Identifier('room'),
                pkey=sql.Identifier('room_dbid')
                )
            self.cursor.execute(query, (curr_room,))
            record = self.cursor.fetchall()
            self.conn.commit()
            if record is not None:
                rules = record[0]
                rule = rules[0]
            else:
                rule = "no rules lel"
            return rule

    async def store_room_data(self, curr_room, info, update):
        nah = 'f'
        logger.info(f"adding {info} for {curr_room}")
        if info == "room_greeting":
            sqlreq = """
                    INSERT INTO ROOM (room_dbid, room_greeting, is_listed)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (room_dbid) DO UPDATE
                    SET room_greeting = (EXCLUDED.room_greeting);
                    """
            self.cursor.execute(sqlreq, (curr_room, update, nah))
        else:
            sqlreq = """
                    INSERT INTO ROOM (room_dbid, room_rules, is_listed)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (room_dbid) DO UPDATE
                    SET room_rules = (EXCLUDED.room_rules);
                    """
            self.cursor.execute(sqlreq, (curr_room, update, nah))

    def get_public_rooms(self):
        query = """
                SELECT room_dbid
                FROM room
                WHERE is_listed = TRUE
                """
        self.cursor.execute(query)
        row = self.cursor.fetchall()
        public = []
        for x in row:
            room_dbid = x[0]
            public.append(room_dbid)
        return public

    def toggle_room_public(self, curr_room):
        query = sql.SQL("select {field} from {table} where {pkey} = %s").format(
                field=sql.Identifier('room_greeting'),
                table=sql.Identifier('room'),
                pkey=sql.Identifier('room_dbid')
                )
        self.cursor.execute(query, (curr_room,))
        record = self.cursor.fetchall()
        self.conn.commit()
        if record is not None:
            command = sql.SQL("update {table} set {field} = NOT {field} WHERE {pkey} = %s").format(
                    field=sql.Identifier('is_listed'),
                    table=sql.Identifier('room'),
                    pkey=sql.Identifier('room_dbid')
                    )
            self.cursor.execute(command, (curr_room,))
            self.conn.commit()
            return record
        else:
            logger.info("room not set up")

    def delete_room_data(self, curr_room):
        self.cursor.execute("DELETE FROM room WHERE (room_dbid) = %s", (curr_room))
