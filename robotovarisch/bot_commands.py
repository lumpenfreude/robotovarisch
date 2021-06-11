import logging

from robotovarisch.chat_functions import send_text_to_room, change_avatar, change_displayname
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
        elif self.command.startswith("help"):
            await self._show_help()
        elif self.command.startswith("avatar"):
            await self._avatar()
        elif self.command.startswith("nick"):
            await self._nick()
        elif self.command.startswith("admin"):
            await self._admin_stuff()
        elif self.command.startswith("rules"):
            await self._get_rules()
        elif self.command.startswith("hello"):
            await self._get_greeting()
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
    
    async def _admin_stuff(self):
        if self.event.sender == "@elen:nopasaran.gq":
            if not self.args:
                text = "Try `admin rules` to change the rules, `admin greeting` to change the greeting, `admin toggle greeting` to turn the greeting on or off, and `admin toggle listed` to be listed in the bot menu."
            topic = self.args[0]
            if topic == "rules":
                field = "room_rules"
                info = " ".join(self.args)
                self.store.save_room_data(field, info)
            elif topic == "greeting":
                field = room_greeting
                info = " ".join(self.args)
                self.store.save_room_data(field, info)
            elif topic == "toggle":
                toggled = self.args[1]
                if toggled == "greeting":
                    field = "greeting_enabled"
                    self.store.toggle_room_setting(field)
                else:
                    text = "`Ye cannot toggle ye flaske`"
                    self.send_text_to_room(self.client, self.room.room_id, text)
            else:
                text = "`Ye cannot adminne ye flaske`"
                self.send_text_to_room(self.client, self.room.room_id, text)

    async def _get_rules(self):
        field = "room_rules"
        record = self.store.load_room_data(field)
        logger.info(f"retrieved {record} from {self.room.room_id}")

    async def _get_greeting(self):
        field = "room_greeting"
        record = self.store.load_room_data(field)
        logger.info(f"retrieved {record} from {self.room.room_id}")
        field = "greeting_enabled"
        record = self.store.load_room_data(field)
        logger.info(f"retrieved {record} from {self.room.room_id}")
    async def _echo(self):
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)
    
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
            text = "Gimme a bit on this lol"
        else:
            text = "Unknown help topic!"
        await send_text_to_room(self.client, self.room.room_id, text)

