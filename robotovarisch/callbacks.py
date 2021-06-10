import logging


from robotovarisch.bot_commands import Command
from robotovarisch.message_responses import Message
from robotovarisch.inv_routine import Invitation
from robotovarisch.storage import Storage
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

    async def message(self, room, event):
        """Callback for when a message event is received

        Args:
            room (nio.rooms.MatrixRoom): The room the event came from

            event (nio.events.room_events.RoomMessageText): The event defining the message

        """
        # Extract the message text
        msg = event.body

        # Ignore messages from ourselves
        if event.sender == self.client.user:
            return

        logger.debug(
            f"Bot message received for room {room.display_name} | "
            f"{room.user_name(event.sender)}: {msg}"
        )

        # Process as message if in a public room without command prefix
        has_command_prefix = msg.startswith(self.command_prefix)
        # room.is_group is often a DM, but not always.
        # room.is_group does not allow room aliases
        # room.member_count > 2 ... we assume a public room
        # room.member_count <= 2 ... we assume a DM
        if not has_command_prefix and room.member_count > 2:
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

    async def roommember(self, room, event):
        if event.sender == self.client.user:
            return
        if event.membership == "join" and event.prev_membership != "join":
            working_room = event.membership.room_id
            await self._welcome()

    async def invite(self, room, event):
        logger.info(f"Invited to {room.room_id}, creating database entries.")
        self.store.on_room_join()
        invitation = Invitation(self.client, self.store, self.config, event.content, room, event)
        await invitation.process()

    async def _welcome(self, working_room):
        greeting = "room_greeting"
        can_greet = self.store.load_room_data("greeting_enabled", working_room)
        if can_greet == "TRUE":
            hello = self.store.load_room_data("room_greeting", working_room)
            await send_text_to_room(self.client, working_room, hello)
