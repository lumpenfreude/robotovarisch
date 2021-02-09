import logging


from robotovarisch.chat_functions import send_text_to_room
logger = logging.getLogger(__name__)


class Event(object):
    def __init__(self, client, store, config, content, room, event):
        self.client = client
        self.store = store
        self.config = config
        self.content = content
        self.room = room
        self.event = event

    async def process(self):
        if self.event.membership == "join" and self.event.prev_membership != "join":
            await self._welcome()

    async def _welcome(self):
        curr_room = self.room.room_id
        greeting = "room_greeting"
        try:
            room = self.store.load_room_data(curr_room, greeting)
            await send_text_to_room(self.client, curr_room, room)
        except AttributeError:
            logger.info("yeah something messed up idk")
