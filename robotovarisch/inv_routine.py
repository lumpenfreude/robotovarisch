import logging
from nio import JoinError
logger = logging.getLogger(__name__)


class Invitation(object):
    def __init__(self, client, store, config, content, room, event):
        self.client = client
        self.store = store
        self.config = config
        self.content = content
        self.room = room
        self.event = event

    async def process(self):
        for attempt in range(3):
            result = await self.client.join(self.room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {self.room.room_id} (attempt %d): %s",
                    attempt,
                    result.message,
                )
            else:
                break
        else:
            logger.error("Unable to join room: %s", self.room.room_id)
        self.store.on_room_join()
        logger.info(f"joined {self.room.room_id}")
