import logging
logger = logging.getLogger(__name__)

from robotovarisch.chat_functions import send_text_to_room

class Memberchange(object):
    def __init__(self, client, store, config, content, room, event, working_room):
        self.client = client
        self.store = store
        self.config = config
        self.content = content
        self.room = room
        self.event = event
        self.wroom = working_room

    async def process(self, working_room):
        can_greet = self.store.load_room_data("greeting_enabled", self.wroom)
        if can_greet is True:
            hello = self.store.load_room_data("room_greeting", self.wroom)
            await send_text_to_room(self.client, self.wroom, hello)


