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


