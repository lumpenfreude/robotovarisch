from robotovarisch.chat_functions import send_text_to_room
from robotovarisch.storage import Storage


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
        room = self.load_room_data(self.event.room_id)
        await send_text_to_room(self.client, self.room.room_id, room.room_greeting)
