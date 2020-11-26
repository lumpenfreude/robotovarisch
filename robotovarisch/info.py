from robotovarisch.chat_functions import send_text_to_room


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
        rooms = self.store.load_room_data()
        for room in rooms:
            if room.room_dbid == curr_room:
                await send_text_to_room(self.client, self.room.room_id, room.room_greeting)
