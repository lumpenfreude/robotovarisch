import logging
import random

from nio import PowerLevels as pl
from robotovarisch.chat_functions import send_text_to_room, send_junk_to_room, change_avatar, change_displayname
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
        elif self.command.startswith("roll"):
            await self._rolldice()
        elif self.command.startswith("avatar"):
            await self._avatar()
        elif self.command.startswith("nick"):
            await self._nick()
        elif self.command.startswith("getpowerlevel"):
            await self._get_power_level()
        elif self.command.startswith("addroomgreet"):
            await self._add_room_greeting()
        elif self.command.startswith("delroomgreet"):
            await self._del_room_data()
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

    async def _toggle_public(self):
        usrlvl = pl.get_user_level(self.room.power_levels, self.event.sender)
        if usrlvl == 100:
            curr_room = self.room.room_id
            self.store.toggle_room_public(curr_room)
            await send_text_to_room(self.client, self.room.room_id, "ok")
        else:
            await send_text_to_room(self.client, self.room.room_id, "you need to be room admin to do that, friendo")


    async def _list_rooms(self):
        text = self.store.get_public_rooms()
        for x in text:
            room_state = await self.client.room_get_state_event(x, "m.room.topic")
            logger.info(room_state)
            await send_text_to_room(self.client, self.room.room_id, "ok")
        await send_text_to_room(self.client, self.room.room_id, "idk man that\'s all i got right now.")

    async def _echo(self):
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _greeting(self):
        info = "room_greeting"
        curr_room = self.room.room_id
        text = self.store.load_room_data(curr_room, info)
        logger.info(f"{text}")
        if text is not None:
            await send_text_to_room(self.client, self.room.room_id, text)

    async def _rules(self):
        info = "room_rules"
        curr_room = self.room.room_id
        text = self.store.load_room_data(curr_room, info)
        if text is not None:
            await send_text_to_room(self.client, self.room.room_id, text)

    async def _add_room_greeting(self):
        usrlvl = pl.get_user_level(self.room.power_levels, self.event.sender)
        logger.info(f"{usrlvl}")
        if usrlvl == 100:
            curr_room = self.room.room_id
            text = " ".join(self.args)
            await self.store.store_room_data(curr_room, "room_greeting", text)
        else:
            await send_text_to_room(self.client, self.room.room_id, "you need to be room admin to do that, friendo")


    async def _add_room_rules(self):
        usrlvl = pl.get_user_level(self.room.power_levels, self.event.sender)
        if usrlvl == 100:
            curr_room = self.room.room_id
            text = " ".join(self.args)
            await self.store.store_room_data(curr_room, "room_rules", text)
        else:
            await send_text_to_room(self.client, self.room.room_id, "you need to be room admin to do that, friendo")

    async def _del_room_data(self):
        usrlvl = pl.get_user_level(self.room, self.event.sender)
        if usrlvl == 100:
            curr_room = self.room.room_id
            await self.store.delete_room_data(curr_room)
        else:
            await send_text_to_room(self.client, self.room.room_id, "no.diggity")

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )

    async def _rolldice(self):
        result = 0
        result_total = ''
        try:
            numdice = self.args.split('d')[0]
            diceval = self.args.split('d')[1]
        except Exception as e:
            print(e)
            await send_text_to_room(self.client, self.room.room_id, "format should be !comrade roll (x)d(y) with the number of dice and the sides being x and y, respectively. and no parentheses.")

        if int(numdice) > 500:
            await send_text_to_room(self.client, self.room.room_id, "oh my god that's so many dice what are you trying to do to me")
        rolls, limit = map(int, self.args.split('d'))

        for r in range(rolls):
            number = random.randint(1, limit)
            result_total = result_total + number
            if result == '':
                result += str(number)
            else:
                result += ', ' + str(number)

        if numdice == '1':
            await send_text_to_room(self.client, self.room.room_id, result)

        else:
            response = result + " Total: " + str(result)
            await send_text_to_room(self.client, self.room.room_id, response)

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
