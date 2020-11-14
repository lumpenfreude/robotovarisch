from robotovarisch.chat_functions import send_text_to_room, send_junk_to_room

class Event(object):
    def __init__(self, client, store, config, content, room, event):
         self.client = client
         self.store = store
         self.config = config
         self.content = content
         self.room = room
         self.event = event

    async def process(self):
        if self.event.membership == "join" and prev_membership != "join":
            await self._welcome()
        elif self.event.membership == "ban":
            await self._mock()
    
    async def _welcome(self):
        welcome = "hello and welcome! this is the lobby of the server, and -- while encrypted -- is largerly unsecured. please watch what you say! this server was originally created for the rifle social on facebook but has grown to encompass many facebook groups and general regions of general leftist organizing. we have rooms like #trs:nopasaran.gq for weapons chatter, #gearposting:nopasaran.gq for gear posting, #support:nopasaran.gq for tech support, and so on! there are further rooms that are invite-only that you will hear all about! to hear more garbage from my robo-mouth, hit me up by typing !comrade before a comment"
        await send_text_to_room(self.client, self.room.room_id, welcome)
    
    async def _ban(self):
        mockery = "christ, what an asshole"
        await send_text_to_room(self.client, self.room.room_id, mockery)
