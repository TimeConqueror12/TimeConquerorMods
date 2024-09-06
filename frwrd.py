import asyncio
from telethon.tl.types import Message
import telethon
from .. import loader, utils

@loader.tds
class AutoForward(loader.Module):
    """Автоматически пересылает сообщения из каналов в один"""
    strings = {
        "name": "AutoForward",
        "channels_from": "Каналы из которых будут пересылаться сообщения",
        "channel_to": "Канал в который будут пересылаться сообщения из каналов"
    }

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._db.set(__name__, "status", False)

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "channels_from",
                [],
                lambda: self.strings("channels_from"),
                validator=loader.validators.Series(
                    validator=loader.validators.Union(
                        loader.validators.Integer(),
                    )
                )
            ),
            loader.ConfigValue(
                "channel_to",
                None,
                lambda: self.strings("channel_to"),
                validator=loader.validators.Integer()
            )
        )

    @loader.command()
    async def autoforward(self, message):
        """- вкл/выкл модуля"""
        status = self._db.get(__name__, "status")
        self._db.set(__name__, "status", not status)
        data = (
            "Пересылаю"
            if self._db.get(__name__, "status")
            else "Больше не пересылаю"
        )

        await utils.answer(message, "<emoji document_id=5416117059207572332>➡️</emoji> <b>{}</b>".format(data))

    @loader.watcher(only_channels=True)
    async def watcher(self, m):
        status = self._db.get(__name__, "status")
        if status:
            if m.chat_id not in self.config["channels_from"]:
                return

            # Отправляем текст сообщения
            text = m.text
            reply_to = m.reply_to_msg_id
            
            if text:
                await self._client.send_message(self.config["channel_to"], text, reply_to=reply_to, link_preview=False)
            
            # Отправляем медиафайлы (если есть)
            if m.media:
                await self._client.send_file(self.config["channel_to"], m.media, reply_to=reply_to)
