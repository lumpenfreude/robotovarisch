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
        await self.store.load_room_data(curr_room)
