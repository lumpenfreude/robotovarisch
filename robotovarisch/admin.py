import logging

from robotovarisch.chat_functions import send_text_to_room, change_avatar, change_displayname
from robotovarisch.storage import Storage
logger = logging.getLogger(__name__)

class Admin(object):
    def __init__(self, client, store, config, msg, room, event, userlevel):
        self.client = client
        self.store = store
        self.config = config
        self.msg = msg
        self.room = room
        self.event = event
        self.userlevel = userlevel
        self.args = self.msg.split()

    async def process(self):
        if self.args[0] == "rules":
            working_room = self.room.room_id
            info = " ".join(self.args).split(" ", 1)[1]
            self.store.update_room_rules(info, working_room)
            newrules = self.store.load_room_data("room_rules", working_room)
            text = "Success! Rules are now: %s" % newrules
            await send_text_to_room(self.client, self.room.room_id, text)
        elif self.args[0] == "greeting":
            working_room = self.room.room_id
            info = " ".join(self.args).split(" ", 1)[1]
            self.store.update_room_greet(info, working_room)
            newgreet = self.store.load_room_data("room_greeting", working_room)
            text = "Success! Greeting is now: %s" % newgreet
            text = "Success."
            await send_text_to_room(self.client, self.room.room_id, text)
        elif self.args[0] == "toggle":
            working_room = self.room.room_id
            if self.args[1]:
                if self.args[1] == "greeting":
                    self.store.toggle_room_setting(working_room)
                    is_on = self.store.load_room_data("greeting_enabled", working_room)
                    if is_on is True:
                        text = "Greeting Enabled."
                    else:
                        text = "Greeting Disabled"
                        await send_text_to_room(self.client, self.room.room_id, text)
            else:
                text = "`Ye cannot toggle ye flaske`"
                await send_text_to_room(self.client, self.room.room_id, text)
        else:
            text = "`Ye cannot adminne ye flaske`"
            await send_text_to_room(self.client, self.room.room_id, text)
