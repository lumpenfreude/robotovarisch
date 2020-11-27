import logging

from robotovarisch.chat_functions import send_text_to_room, send_junk_to_room, change_avatar, change_displayname
from robotovarisch.storage import Dbroom
logger = logging.getLogger(__name__)


class Command(object):
    def __init__(self, client, store, config, command, room, event):
        self.client = client
        self.store = store
        self.config = config
        self.command = command
        self.room = room
        self.event = event
        self.args = self.command.split()[1:]

    async def process(self):
        if self.command.startswith("echo"):
            await self._echo()
        elif self.command.startswith("rooms"):
            await self._list_rooms()
        elif self.command.startswith("rules"):
            await self._rules()
        elif self.command.startswith("greeting"):
            await self._greeting()
        elif self.command.startswith("help"):
            await self._show_help()
        elif self.command.startswith("bonk"):
            await self._bonk()
        elif self.command.startswith("status"):
            await self._status()
        elif self.command.startswith("comfort"):
            await self._comfort()
        elif self.command.startswith("avatar"):
            await self._avatar()
        elif self.command.startswith("nick"):
            await self._nick()
        elif self.command.startswith("addroomgreet"):
            await self._add_room_greeting()
        elif self.command.startswith("delroomgreet"):
            await self._del_room_info()
        elif self.command.startswith("addroomrules"):
            await self._add_room_rules()
        elif self.command.startswith("togglepublic"):
            await self._toggle_public()
        else:
            await self._unknown_command()

    async def _nick(self):
        if self.event.sender == "@elen:nopasaran.gq":
            nick = " ".join(self.args)
            await change_displayname(self.client, nick)

    async def _avatar(self):
        if self.event.sender == "@elen:nopasaran.gq":
            mxid = self.args[0]
            if len(mxid) > 6 and mxid[0:6] == "mxc://":
                await change_avatar(self.client, mxid)
            else:
                await send_text_to_room(self.client, self.room.room_id, "that's not an mxc url")

    async def _list_rooms(self):
        text = "alad awaiting implemebtation lol holy fucj typijg wuthiut autocorrect is hard i think i meed a sialing wand"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _echo(self):
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)

        async def _greeting(self):
        text = self.store.get_room_greeting(self.room.room_id)
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _rules(self):
        text = self.store.get_room_rules(self.room.room_id)
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _add_room_greeting(self):
        if self.event.sender == "@elen:nopasaran.gq":
            curr_room = self.room.room_id
            text = " ".join(self.args)
            await self.store.store_room_data(curr_room, text)

    async def _add_room_rules(self):
        if self.event.sender == "@elen:nopasaran.gq":
            curr_room = self.room.room_id
            text = " ".join(self.args)
            await self.store.store_room_data(curr_room, text)

    async def _del_room_info(self):
        if self.event.sender == "@elen:nopasaran.gq":
            await self.store.delete_room_data(self.event.room_id)
        else:
            await send_text_to_room(self.client, self.room.room_id, "no.diggity")

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )

    async def _show_help(self):
        if not self.args:
            text = (
                "Hello, I am a bot made with matrix-nio! Use `help commands` to view "
                "available commands."
            )
            await send_text_to_room(self.client, self.room.room_id, text)
            return

        topic = self.args[0]
        if topic == "rules":
            text = "be fucking cool lmao. each room has its own rules. follow them or you will be booted. however, ***nowhere*** on this server is bigotry tolerated. if you see it, alert @elen:nopasaran.gq (the server administrator) please."
        elif topic == "commands":
            text = "Available commands: `rooms` list public-ish rooms `status` check the status of a politician to see if they are alive or dead. `echo` echo a statement. `help` see the help menu. `commands` see this shit. `bonk` to stop the horney. `comfort` comfort a sad comrade. `intro` give the intro spiel again"
        elif topic == "rooms":
            text = "coming soon lol"
        else:
            text = "Unknown help topic!"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _bonk(self):
        content = {
                    "body": "NO MORE HORNEY DOT JPEG.jpeg",
                    "info": {
                        "size": 36393,
                        "mimetype": "image/jpeg",
                        "thumbnail_info": None,
                        "w": 700,
                        "h": 478,
                        "thumbnail_url": None,
                        },
                    "msgtype": "m.image",
                    "url": "mxc://nopasaran.gq/DKtefusRXBxmzWgoaKdyiXlq",
                    }
        await send_junk_to_room(self.client, self.room.room_id, content)

    async def _comfort(self):
        content = {
                "body": "not alone.jpg",
                "info": {
                    "size": 12269,
                    "mimetype": "image/jpeg",
                    "thumbnail_info": None,
                    "w": 500,
                    "h": 240,
                    "thumbnail_url": None,
                    },
                "msgtype": "m.image",
                "url": "mxc://nopasaran.gq/sOVAcvkPQHOKezYpoCEOkvXp",
                }
        await send_junk_to_room(self.client, self.room.room_id, content)
