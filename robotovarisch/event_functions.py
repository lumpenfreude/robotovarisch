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
        if self.event.membership == "join" and self.event.prev_membership != "join":
            await self._welcome()
        elif self.event.membership == "ban":
            await self._mock()
    
    async def _welcome(self):
        welcome = "Henlo and welcome to the rifle social room, the lobby for nopasaran.gq. This is a community controlled, end to end encrypted messaging service which started as a parachute for the fb group The Rifle Social. While we strive to make things as secure as we can, this is still an unvetted public room that anyone with an account can see. Ixnay on the illkay the esidentpray. I am Robo-Tovarisch, your robot host. I'm here to assist you in navigating this server. If you'd like me to list what I can do for you, type “!comrade help commands”. In addition to this lobby there are a multitude of public topical and regional community rooms you can join. If you'd like me to list available public rooms, type “!comrade rooms”.  The server has one rule: be fucking cool lmao ***nowhere*** on this server is bigotry tolerated. If you see it, alert @elen:nopasaran.gq (the server administrator), or your local group admin. Other rooms may have their own  specific rules, so follow them or be booted." 
        await send_text_to_room(self.client, self.room.room_id, welcome)
    
    async def _ban(self):
        mockery = "christ, what an asshole"
        await send_text_to_room(self.client, self.room.room_id, mockery)
