import logging

from functools import reduce
from nio.rooms import MatrixUser
from robotovarisch.bot_commands import Command
from robotovarisch.message_responses import Message
from robotovarisch.inv_routine import Invitation
from robotovarisch.memberchange import Memberchange
from robotovarisch.admin import Admin

logger = logging.getLogger(__name__)


class Callbacks(object):
    def __init__(self, client, store, config):
        """
        Args:
            client (nio.AsyncClient): nio client used to interact with matrix

            store (Storage): Bot storage

            config (Config): Bot configuration parameters
        """
        self.client = client
        self.store = store
        self.config = config
        self.command_prefix = config.command_prefix
        self.admin_prefix = config.admin_prefix
        self.user = MatrixUser

    async def message(self, room, event):
        def parse_data(roomid):
             for key, value in roomid.items():
                 if isinstance(value, dict):
                     for pair in parse_data(value):
                         yield (key, *pair)
                 else:
                     yield (key, value)

        # Extract the message text
        msg = event.body

        # Ignore messages from ourselves
        if event.sender == self.client.user:
            return

        logger.info(
            f"Bot message received for room {room.display_name} | "
            f"{room.user_name(event.sender)}: {msg}"
        )

        # Process as message if in a public room without command prefix
        has_command_prefix = msg.startswith(self.command_prefix)
        has_admin_prefix = msg.startswith(self.admin_prefix)
        # room.is_group is often a DM, but not always.
        # room.is_group does not allow room aliases
        # room.member_count > 2 ... we assume a public room
        # room.member_count <= 2 ... we assume a DM
        if not has_command_prefix and not has_admin_prefix and room.member_count > 2:
            # General message listener
            message = Message(self.client, self.store, self.config, msg, room, event)
            await message.process()
            return

        # Otherwise if this is in a 1-1 with the bot or features a command prefix,
        # treat it as a command
        if has_command_prefix:
            # Remove the command prefix
            msg = msg[len(self.command_prefix) :]
            command = Command(self.client, self.store, self.config, msg, room, event)
            await command.process()
            return

        if has_admin_prefix:
            msg = msg[len(self.comnd_prefix) :]
            roomstate = await self.client.room_get_state(room.room_id)
            for sublist in roomstate.events:
                if sublist['type'] == 'm.room.power_levels':
                    power_users = sublist['content']['users']
                    if power_users[event.sender]:
                        if power_users[event.sender] == '50':
                            userlevel = "mod"
                            admin = Admin(self.client, self.store, self.config, msg, room, event, userlevel)
                            await admin.process()
                            return
                        if power_users[event.sender] == '100':
                            userlevel = "admin"
                            admin   = Admin(self.client, self.store, self.config, msg, room, event, userlevel)
                            await admin.process()
                            return
                        else:
                            return

            
            #await admin.process()
            return

    async def roommember(self, room, event):
        if event.sender == self.client.user:
            return
        if event.membership == "join" and event.prev_membership != "join":
            working_room = room.room_id
            memberchange = Memberchange(self.client, self.store, self.config, event.content, room, event, working_room)
            await memberchange.process(working_room)

    async def invite(self, room, event):
        logger.info(f"Invited to {room.room_id}, creating database entries.")
        invitation = Invitation(self.client, self.store, self.config, event.content, room, event)
        await invitation.process()

