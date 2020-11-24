from nio import AsyncClient


class Room(object):
    """
    an object containing information about a room, pulled from postgres
    Args:
        client: matrix client
        store: Storage object
        room_dbid: the id of the room the room greeting should appear in
        room_greeting: the greeting for the room from the db
        room_rules: the rules from the room from the db
        is_listed: a boolean value for whether the room is listed with the bot

    """

    def __init__(
        self,
        client: AsyncClient,
        room_dbid: str,
        room_greeting: str,
        room_rules: str,
        is_listed: bool,
    ):
        self.client = client
        self.room_dbid = room_dbid
        self.room_greeting = room_greeting
        self.room_rules = room_rules
        self.is_listed = is_listed
