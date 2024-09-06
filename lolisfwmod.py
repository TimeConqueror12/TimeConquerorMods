#
#████████╗██╗███╗░░░███╗███████╗░█████╗░░█████╗░███╗░░██╗░██████╗░███████╗██████╗░░█████╗░██████╗░
#╚══██╔══╝██║████╗░████║██╔════╝██╔══██╗██╔══██╗████╗░██║██╔═══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗
#░░░██║░░░██║██╔████╔██║█████╗░░██║░░╚═╝██║░░██║██╔██╗██║██║██╗██║█████╗░░██████╔╝██║░░██║██████╔╝
#░░░██║░░░██║██║╚██╔╝██║██╔══╝░░██║░░██╗██║░░██║██║╚████║╚██████╔╝██╔══╝░░██╔══██╗██║░░██║██╔══██╗
#░░░██║░░░██║██║░╚═╝░██║███████╗╚█████╔╝╚█████╔╝██║░╚███║░╚═██╔═╝░███████╗██║░░██║╚█████╔╝██║░░██║
#░░░╚═╝░░░╚═╝╚═╝░░░░░╚═╝╚══════╝░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝

# meta developer: @minovayIa_a

import logging
import random
from .. import loader, utils

logger = logging.getLogger("LoliSFW")

@loader.tds
class lolisfw(loader.Module):
    """Лучший кастомный мод с лолями #2 :3"""
    strings = {
        "name": "LoliSFW",
        "loading_photo": "<emoji document_id=5215327832040811010>⏳</emoji> <b>Загружаю фоточку</b>",
        "error_loading": "<b>Чёта не получилось..</b>",
        "sending_photo": "<b>Кидаю фоточку...</b>",
        "photo_name": "<b>Имя файла: {}</b>"
    }

    async def lolisfcmd(self, message):
        """кидает фото с лолями(наверное не порнушку)"""
        await utils.answer(message, self.strings("loading_photo"))
        await self._send_random_photo_from_channel(message, channel_username="loliconchikl")

    async def _send_random_photo_from_channel(self, message, channel_username, as_file=False):
        try:
            channel_entity = await message.client.get_entity(channel_username)
            messages = await message.client.get_messages(channel_entity, limit=100)

            photos = [msg for msg in messages if msg.photo]
            if not photos:
                await utils.answer(message, self.strings("error_loading"))
                return

            photo = random.choice(photos)

            if as_file:
                await message.client.send_file(
                    message.peer_id,
                    file=photo,
                    caption=self.strings("photo_name").format(channel_username),
                    force_document=True  # Send as a file without compression
                )
            else:
                await message.client.send_file(
                    message.peer_id,
                    file=photo,
                    caption=self.strings("photo_name").format(channel_username)
                )

            await message.delete()

        except Exception as e:
            logger.error(f"Error fetching photo from channel {channel_username}: {e}")
            await utils.answer(message, self.strings("error_loading"))

