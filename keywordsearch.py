import asyncio
from telethon.tl.types import Message
import telethon
from .. import loader, utils

@loader.tds
class KeywordSearch(loader.Module):
    """Автоматически пересылает сообщения с указанными хештегами/ключевыми словами из одного канала в другой"""
    strings = {
        "name": "KeywordSearch",
        "searching_in": "Канал для поиска сообщений",
        "forwarding_to": "Канал для пересылки сообщений",
        "forward_started": "Начинаю пересылку сообщений...",
        "forward_stopped": "Пересылка остановлена."
    }

    def __init__(self):
        self.config = loader.ModuleConfig()

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._db.set(__name__, "forwarding", False)  # Изначально пересылка выключена

    async def resolve_entity(self, entity):
        """Разрешение сущности для поддержки приватных ссылок"""
        if entity.startswith('https://t.me/'):
            return await self._client.get_entity(entity)
        return await self._client.get_entity(entity.strip('@'))

    @loader.command()
    async def kws(self, message):
        """Ищет по хештегам и исключает по заданным хештегам. Пример: .kws @канал_источник @канал_назначение #хештег1 [#хештег2 ...] $хештег3 [$хештег4 ...]"""
        args = utils.get_args(message)
        if len(args) < 3:
            await utils.answer(message, "<b>Укажите каналы и хотя бы один хештег!</b>\nПример: .kws @channel1 @channel2 #hashtag1 $hashtag2")
            return

        source_channel = await self.resolve_entity(args[0])
        dest_channel = await self.resolve_entity(args[1])
        hashtags = [arg for arg in args[2:] if arg.startswith('#')]
        excluded_tags = [arg[1:] for arg in args[2:] if arg.startswith('$')]

        if not hashtags:
            await utils.answer(message, "<b>Укажите хотя бы один хештег для поиска!</b>")
            return

        # Включаем флаг пересылки
        self._db.set(__name__, "forwarding", True)

        await utils.answer(message, f"<b>Ищу сообщения с хештегами {', '.join(hashtags)} и исключая {', '.join(excluded_tags)} в {source_channel.title} и пересылаю в {dest_channel.title}</b>")

        # Поиск и пересылка сообщений
        await self.search_and_forward(source_channel, dest_channel, hashtags, excluded_tags)

    @loader.command()
    async def wkws(self, message):
        """Ищет по ключевым словам и исключает по заданным словам. Пример: .wkws @канал_источник @канал_назначение #хештег1 [#хештег2 ...] $хештег3 [$хештег4 ...]"""
        args = utils.get_args(message)
        if len(args) < 3:
            await utils.answer(message, "<b>Укажите каналы и хотя бы одно ключевое слово!</b>\nПример: .wkws @channel1 @channel2 #keyword1 $keyword2")
            return

        source_channel = await self.resolve_entity(args[0])
        dest_channel = await self.resolve_entity(args[1])
        keywords = [arg for arg in args[2:] if arg.startswith('#')]
        excluded_keywords = [arg[1:] for arg in args[2:] if arg.startswith('$')]

        if not keywords:
            await utils.answer(message, "<b>Укажите хотя бы одно ключевое слово для поиска!</b>")
            return

        # Включаем флаг пересылки
        self._db.set(__name__, "forwarding", True)

        await utils.answer(message, f"<b>Ищу сообщения с ключевыми словами {', '.join(keywords)} и исключая {', '.join(excluded_keywords)} в {source_channel.title} и пересылаю в {dest_channel.title}</b>")

        # Поиск и пересылка сообщений
        await self.search_and_forward(source_channel, dest_channel, keywords, excluded_keywords)

    @loader.command()
    async def kwsstop(self, message):
        """Останавливает пересылку сообщений"""
        self._db.set(__name__, "forwarding", False)
        await utils.answer(message, "<b>Пересылка сообщений остановлена.</b>")

    async def search_and_forward(self, source_channel, dest_channel, keywords, excluded_keywords):
        """Ищет все сообщения по ключевым словам или хештегам в канале и пересылает их"""
        async for msg in self._client.iter_messages(source_channel):
            if not self._db.get(__name__, "forwarding"):
                await self._client.send_message(dest_channel, self.strings["forward_stopped"])
                break

            if msg.raw_text:
                text = msg.raw_text

                # Условие включения ключевых слов/хештегов
                if all(keyword in text for keyword in keywords) and not any(excluded in text for excluded in excluded_keywords):
                    reply_to = msg.reply_to_msg_id

                    # Пересылаем текст и медиа в одном сообщении
                    if msg.media:
                        caption = msg.raw_text if msg.raw_text else ""
                        await self._client.send_file(dest_channel, msg.media, caption=caption, reply_to=reply_to)
                    else:
                        if msg.raw_text:
                            await self._client.send_message(dest_channel, msg.raw_text, reply_to=reply_to, link_preview=False)

        # Если пересылка не была остановлена
        if self._db.get(__name__, "forwarding"):
            await self._client.send_message(dest_channel, f"<b>Все сообщения с ключевыми словами/хештегами пересланы.</b>")
