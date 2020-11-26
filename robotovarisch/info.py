import logging

from robotovarisch.chat_functions import send_text_to_room
logger = logging.getLogger(__name__)


class Info(object):
    def __init__(self, client, store, config, content, room, event):
        self.client = client
        self.store = store
        self.config = config
        self.content = content
        self.room = room
        self.event = event

    async def welcome(self):
        curr_room = self.room.room_id
        dbrooms = self.store.load_room_data()
        for v in range(len(dbrooms)):
            if curr_room == dbroom[0]:
                logger.info(f"{dbroom[0]} vs {curr_room}, greeting is {dbroom[1]}")

                await send_text_to_room(self.client, self.room.room_id, dbroom[1])
