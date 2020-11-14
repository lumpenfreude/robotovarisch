import logging

from markdown import markdown
from nio import SendRetryError, AsyncClient, HttpClient

logger = logging.getLogger(__name__)


async def send_text_to_room(
    client, room_id, message, notice=True, markdown_convert=True
):
    msgtype = "m.notice" if notice else "m.text"

    content = {
        "msgtype": msgtype,
        "format": "org.matrix.custom.html",
        "body": message,
    }

    if markdown_convert:
        content["formatted_body"] = markdown(message)

    try:
        await client.room_send(
            room_id, "m.room.message", content, ignore_unverified_devices=True,
        )
    except SendRetryError:
        logger.exception(f"Unable to send message response to {room_id}")

async def send_junk_to_room(client, room_id, content):
    try:
        await client.room_send(room_id, "m.room.message", content, ignore_unverified_devices=True,)
    except SendRetryError:
        logger.exception(f"who knows lol")

async def change_avatar(client, mxid):
    await client.set_avatar(mxid)

async def change_displayname(client, name):
    await client.set_displayname(name)
