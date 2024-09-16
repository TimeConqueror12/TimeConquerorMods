#
#████████╗██╗███╗░░░███╗███████╗░█████╗░░█████╗░███╗░░██╗░██████╗░███████╗██████╗░░█████╗░██████╗░
#╚══██╔══╝██║████╗░████║██╔════╝██╔══██╗██╔══██╗████╗░██║██╔═══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗
#░░░██║░░░██║██╔████╔██║█████╗░░██║░░╚═╝██║░░██║██╔██╗██║██║██╗██║█████╗░░██████╔╝██║░░██║██████╔╝
#░░░██║░░░██║██║╚██╔╝██║██╔══╝░░██║░░██╗██║░░██║██║╚████║╚██████╔╝██╔══╝░░██╔══██╗██║░░██║██╔══██╗
#░░░██║░░░██║██║░╚═╝░██║███████╗╚█████╔╝╚█████╔╝██║░╚███║░╚═██╔═╝░███████╗██║░░██║╚█████╔╝██║░░██║
#░░░╚═╝░░░╚═╝╚═╝░░░░░╚═╝╚══════╝░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝

# meta developer: @minovayIa_a

import logging
from telethon.tl.types import Message, PeerUser
from telethon.tl.functions.contacts import BlockRequest
from telethon.utils import get_display_name

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class PMBLplusMod(loader.Module):
    """Доп. мод для PMBL. см. конфиг."""

    strings = {
        "name": "PMBLplus",
        "flood_banned": "<emoji document_id=5210952531676504517>❌</emoji> <b>Сообщение пользователя {}</b> содержит запрещенные слова и было удалено.",
        "phrase_added": "<emoji document_id=5397916757333654639>➕</emoji> <b>Фраза добавлена в список модерации.</b>",
        "phrase_removed": "<emoji document_id=5206607081334906820>✔️</emoji> <b>Фраза удалена из списка модерации.</b>",
        "no_phrases": "<emoji document_id=5447644880824181073>⚠️</emoji> <b>Список модерации пуст.</b>",
        "current_phrases": "<emoji document_id=5334882760735598374>📝</emoji> <b>Текущие фразы для модерации:</b>\n{}",
        "args_flood": "<emoji document_id=5240241223632954241>🚫</emoji> <b>Пример использования:</b> <code>.pmblfloodadd фраза</code>",
        "blocked_user": "<emoji document_id=5240241223632954241>🚫</emoji> <b>Пользователь {} был заблокирован за нарушение.</b>",
        "not_blocked": "<emoji document_id=5274099962655816924>❗️</emoji> <b>Пользователь не был заблокирован, согласно настройкам.</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "forbidden_phrases",
                [],
                lambda: "Список банвордов",
                validator=loader.validators.Series(loader.validators.String()),
            ),
            loader.ConfigValue(
                "moderate_flood",
                True,
                lambda: "Модерировать входящие сообщения?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "dialog_min_msg",
                1,
                lambda: "Минимальное количество сообщений для игнорирования пользователя\nСоздано для того, чтобы скрипт не трогал пользователей с которыми уже был диалог.",
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "block_user",
                True,
                lambda: "Блокировать пользователя при нарушении?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_response",
                "None",
                lambda: "Кастомный ответ для пользователя при нарушении",
                validator=loader.validators.String(),
            ),
        )

    async def addwordcmd(self, message: Message):
        """Выводит текущие фразы для модерации и добавляет новые"""
        args = utils.get_args_raw(message)
        
        if not args:
            phrases = self.config["forbidden_phrases"]
            if phrases:
                await utils.answer(message, self.strings("current_phrases").format("\n".join(f"- {p}" for p in phrases)))
            else:
                await utils.answer(message, self.strings("no_phrases"))
            return
        
        # Добавление новой фразы
        phrases = self.config["forbidden_phrases"]
        if args not in phrases:
            phrases.append(args)
            self.set("forbidden_phrases", phrases)
            await utils.answer(message, self.strings("phrase_added"))
        else:
            await utils.answer(message, f"<emoji document_id=5447644880824181073>⚠️</emoji> <b>Фраза '{args}' уже добавлена.</b>")
    
    async def rmwordcmd(self, message: Message):
        """Удаляет фразу из списка модерации"""
        args = utils.get_args_raw(message)
        phrases = self.config["forbidden_phrases"]
        
        if args in phrases:
            phrases.remove(args)
            self.set("forbidden_phrases", phrases)
            await utils.answer(message, self.strings("phrase_removed"))
        else:
            await utils.answer(message, f"<emoji document_id=5447644880824181073>⚠️</emoji> <b>Фраза '{args}' не найдена в списке.</b>")

    async def watcher(self, message: Message):
        """Отслеживает входящие сообщения и удаляет их, если они содержат запрещенные фразы"""
        if not self.config["moderate_flood"]:
            return

        if (
            getattr(message, "out", False)
            or not isinstance(message, Message)
            or not isinstance(message.peer_id, PeerUser)
        ):
            return

        # Проверка на количество сообщений в диалоге
        peer_id = message.peer_id
        message_count = 0

        async for msg in self._client.iter_messages(peer_id, limit=100):
            if msg.sender_id == self._tg_id or msg.sender_id == message.sender_id:
                message_count += 1
            if message_count >= self.config["dialog_min_msg"]:
                return  # Если сообщений больше заданного порога, игнорируем модерацию

        forbidden_phrases = self.config["forbidden_phrases"]
        if any(phrase.lower() in message.raw_text.lower() for phrase in forbidden_phrases):
            await message.delete()
            custom_response = self.config["custom_response"]
            await utils.answer(message, f"<b>{custom_response}</b>")

            if self.config["block_user"]:
                await self._client(BlockRequest(id=message.sender_id))
                await utils.answer(message, self.strings("blocked_user").format(get_display_name(message.sender)))
            else:
                await utils.answer(message, self.strings("not_blocked"))
