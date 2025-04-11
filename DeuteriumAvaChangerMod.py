# meta developer: @minovayIa_a | @DeuteriumModules

# В чужих кодах роешься, пупсик?

import asyncio
import random
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from .. import loader, utils

async def download_media(event, client):
    media = await event.get_reply_message()
    if media and media.media:
        path = await client.download_media(media, "avatar.jpg")
        return path
    return None

@loader.tds
class AvaChanger(loader.Module):
    """Модуль для установки аватарки в ответ на фото"""
    strings = {
        "name": "AvaChanger",
        "ava_failed": "⚠️ Не удалось скачать медиа. Ответьте на фото.",
        "ava_changing": "🔄 Устанавливаю новое фото...",
        "ava_changed": "✅ Аватар обновлён!",
        "ava_flood_wait": "🚫 Слишком много попыток! Повторю через {} секунд.",
    }

    async def client_ready(self, client, db):
        self._client = client

    @loader.command()
    async def ava(self, message):
        """Ответьте на фото, чтобы установить его как аватар"""
        path = await download_media(message, self._client)
        if not path:
            await utils.answer(message, self.strings("ava_failed"))
            return

        await utils.answer(message, self.strings("ava_changing"))
        try:
            await self._client(UploadProfilePhotoRequest(file=await self._client.upload_file(path)))
            await utils.answer(message, self.strings("ava_changed"))
        except FloodWaitError as e:
            await utils.answer(message, self.strings("ava_flood_wait").format(e.seconds))
            await asyncio.sleep(e.seconds)
        except RPCError as e:
            await utils.answer(message, f"❌ Ошибка: {e}")

