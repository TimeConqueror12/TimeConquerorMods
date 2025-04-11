# meta developer: @minovayIa_a | @DeuteriumModules

# В чужих кодах роешься, пупсик?

from telethon import functions
from telethon.tl.types import Message
import asyncio
import re
import logging

from .. import loader, utils  

logger = logging.getLogger(__name__)

@loader.tds
class YTdlMod(loader.Module):
    """
    ytb-dl
    """

    strings = {
        "name": "ytb-dl",
        "loading": "...",
        "no_args": "А ссылка то где?",
        "start_text": "...",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.ytdl_bot = "@YtbAudioBot"

    async def message_q(
        self,
        text: str,
        user_id: int,
        chat_id: int,
        mark_read: bool = False,
        delete: bool = False,
        ignore_answer: bool = False,
    ):
        """Отправляет сообщение и возвращает ответ"""
        async with self.client.conversation(user_id) as conv:
            msg = await conv.send_message(text)
            responses = []
            while True:
                response = await conv.get_response()  

                logger.info(f"Получено сообщение: {response.text}")  

                if mark_read:
                    await conv.mark_read()

                if delete:
                    await msg.delete()
                    await response.delete()

                if ignore_answer:
                    return response

                if response.media and response.media.document.mime_type.startswith('audio/'):
                    logger.info("Получен аудиофайл, пересылаем...")  
                    await self.client.send_file(chat_id, response.media, caption="")  
                    logger.info("Аудиофайл переслан.")  
                    break  

                await self.client.send_message(chat_id, f"Получен ответ: {response.text}")

            return "\n".join(responses)

    async def ytbcmd(self, message: Message):
        """
        {ссылка}
        """

        if message.reply_to_msg_id:
            replied_message = await message.get_reply_message()
            args = (replied_message.message or "").strip()
            logger.info(f"Полученная ссылка из ответа: {args}") #Debug data
        else:
            args = utils.get_args_raw(message).strip()
            logger.info(f"Полученная ссылка из команды: {args}") #Debug data

        if not args or not args.startswith("http"):
            logger.warning("Аргумент пустой или не является ссылкой.")  
            return await utils.answer(message, self.strings["no_args"])

        response = await self.message_q(
            args, self.ytdl_bot, message.chat_id, mark_read=True, delete=False, ignore_answer=False
        )

        if response:
            await self.client.send_file(message.chat_id, response, caption="")  

        await message.delete()

        if response and response != self.strings["loading"]:
            return await utils.answer(message, self.strings["start_text"])
