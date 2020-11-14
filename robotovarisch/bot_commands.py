from robotovarisch.chat_functions import send_text_to_room, send_junk_to_room, change_avatar, change_displayname

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
        elif self.command.startswith("help"):
            await self._show_help()
        elif self.command.startswith("bonk"):
            await self._bonk()
        elif self.command.startswith("intro"):
            await self._introduction()
        elif self.command.startswith("status"):
            await self._status()
        elif self.command.startswith("comfort"):
            await self._comfort()
        elif self.command.startswith("fuckinavatar"):
            await self._avatar()
        elif self.command.startswith("fuckinnick"):
            await self._nick()
        else:
            await self._unknown_command()

    async def _nick(self):
        nick = " ".join(self.args)
        await change_displayname(self.client, nick)

    async def _avatar(self):
        mxid = self.args[0]
        if len(mxid) > 6 and mxid[0:6] == "mxc://":
            await change_avatar(self.client, mxid)
        else:
            await send_text_to_room(self.client, self.room.room_id, "that's not an mxc url")

    async def _list_rooms(self):
        # this is where i am gonna have to add in the interactive room storage stuff... to come
        response = (
           "<b>THE RIFLE SOCIAL</b><br>"
               "- #trs:nopasaran.gq - general gun/weapon help<br>"
               "- #support:nopasaran.gq - tech support<br>"
               "- #politicsdeathzone:nopasaran.gq - the POLITICS DEATH ZONE<br>"
               "- #groupwatcher:nopasaran.gq - group watching stuff on rabb.it clones<br>"
               "<b>THE RED PREPPERS</b><br>"
               "- #theredpreppers:nopasaran.gq - the red preppers!<br>"
               "<b>REGIONAL</b><br>"
               "- #wiscomrades:nopasaran.gq - wisconsin general<br>"
               "    - #mkecdc:nopasaran.gq - milwaukee community defense coalition<br>"
               "- #freecascadia:nopasaran.gq - cascadia region general"
                )
        await send_text_to_room(self.client, self.room.room_id, response)
        
    async def _echo(self):
        response = " ".join(self.args)
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

    async def _status(self):
        dead_person = self.args[0]
        if dead_person == "reagan":
            text = "Ronald Reagan's current status is: `Dead.`"
        elif dead_person == "thatcher":
            text = "Margaret Thatcher's current status is: `Dead.`"
        elif dead_person == "kennedy":
            text = "JFK's current status is: `Dead.` There are many theories as to who killed him, but the simple truth is: his head just *did* that."
        elif dead_person == "kissinger":
            text = "Thanks to the power contained within the souls of thousands of Cambodian children, Henry Kissinger's current status is: `Alive.`"
        else:
            text = "I'm sorry, I don't have information for that person. Please try again."
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _introduction(self):
        await send_text_to_room(
                self.client,
                self.room.room_id,
                f"**Welcome to No Pasaran,** an anti-fascist secure comms server. Thing. This is the main chat, it is an offshoot of The Rifle Social Facebook group. There is also #trs:nopasaran.gq for weapons discussion, #politicsdeathzone:nopasaran.gq for political discussion, and #support:nopasaran.gq for tech support issues. There are numerous other groups, localblhafdafpaefbealorem ipsem sucj my balls.",
                )
    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )
