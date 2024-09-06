# meta developer: @minovayIa_a
from .. import loader, utils
import asyncio
from telethon import events

@loader.tds
class DelayedMessageMod(loader.Module):
    """Модуль для отложенной отправки сообщений"""
    strings = {"name": "DelayedMessage"}

    async def dlymsgcmd(self, message):
        """Использование: .dlymsg {текст сообщения} {количество сообщений} {время между сообщениями в секундах}"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("Укажите параметры команды.")
            return
        
        try:
            msg_text, count, delay = args.rsplit(maxsplit=2)
            count = int(count)
            delay = int(delay)
        except ValueError:
            await message.edit("Неверный формат параметров.")
            return
        
        await message.delete()  # Удаляем команду из чата

        for _ in range(count):
            await message.client.send_message(message.chat_id, msg_text)
            await asyncio.sleep(delay)

