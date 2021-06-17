import logging

from robotovarisch.chat_functions import send_text_to_room, change_avatar, change_displayname
from robotovarisch.storage import Storage
logger = logging.getLogger(__name__)

class Admin(object):
    def __init__(self, client, store, config, admin, room, event):
        self.client = client
        self.store = store
        self.config = config
        self.admin = admin
        self.room = room
        self.event = event
        self.args = self.admin.split()[1:]

    async def process(self):
        if self.args.startswith == "test":
           await send_text_to_room(self.client, self.room.room_id, "we all good babey")
#        if self.args.startswith == "rules":
#            working_room = self.room.room_id
#            info = " ".join(self.args).split(" ", 1)[1]
#            self.store.update_room_rules(info, working_room)
#            text = "Success."
#            await send_text_to_room(self.client, self.room.room_id, text)
#        elif self.msg.startswith == "greeting":
#            working_room = self.room.room_id
#            info = " ".join(self.args).split(" ", 1)[1]
#            self.store.update_room_greet(info, working_room)
#            text = "Success."
#            await send_text_to_room(self.client, self.room.room_id, text)
#        elif self.msg.startswith == "toggle":
#            working_room = self.room.room_id
#            toggled = args[1]
#            if toggled == "greeting":
#                working_room = self.room.room_id
#                self.store.toggle_room_setting(working_room)
#                text = "okay"
#                await send_text_to_room(self.client, self.room.room_id, text)
#            else:
#                text = "`Ye cannot toggle ye flaske`"
#                await send_text_to_room(self.client, self.room.room_id, text)
#        elif topic == "pl":
#            query = args[1]
#            if re.match("^@[A-Za-z0-9._%+-]+:[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", query):
#                usr = "userid="+self.event.sender
#                powerz = await self.pl.get_user_level(self, usr)
#                if powerz >= 50:
#                    text = "user has elevated powers: {powerz}"
#                    await self.send_text_to_room(self.client, self.room.room_id, text)
#                else:
#                    text = "user does not have elevated powers."
#                    await self.send_text_to_room(self.client, self.room.room_id, text)
#            else:
#                text = "username must be in the '!username:server.url' format"
#        else:
#            text = "`Ye cannot adminne ye flaske`"
#            await send_text_to_room(self.client, self.room.room_id, text)
#     
#     
