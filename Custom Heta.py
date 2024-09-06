#
#████████╗██╗███╗░░░███╗███████╗░█████╗░░█████╗░███╗░░██╗░██████╗░███████╗██████╗░░█████╗░██████╗░
#╚══██╔══╝██║████╗░████║██╔════╝██╔══██╗██╔══██╗████╗░██║██╔═══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗
#░░░██║░░░██║██╔████╔██║█████╗░░██║░░╚═╝██║░░██║██╔██╗██║██║██╗██║█████╗░░██████╔╝██║░░██║██████╔╝
#░░░██║░░░██║██║╚██╔╝██║██╔══╝░░██║░░██╗██║░░██║██║╚████║╚██████╔╝██╔══╝░░██╔══██╗██║░░██║██╔══██╗
#░░░██║░░░██║██║░╚═╝░██║███████╗╚█████╔╝╚█████╔╝██║░╚███║░╚═██╔═╝░███████╗██║░░██║╚█████╔╝██║░░██║
#░░░╚═╝░░░╚═╝╚═╝░░░░░╚═╝╚══════╝░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝

# meta developer: @minovayIa_a

import logging
from .. import loader, utils

logger = logging.getLogger("HetaCustom")

@loader.tds
class HetaCustom(loader.Module):
    """Custom mod of UnitHeta"""
    strings = {
        "name": "UnitHetaCustom",
        "loading_file": "<emoji document_id=5215327832040811010>⏳</emoji> <b>Загрузка...</b>",
        "error_loading": "<b>Не нашёл.. а может возникла ошибка.\nСмотри лог.</b>",
        "sending_file": "<b>Похоже нашёл...</b>",
    }

    async def unithetacmd(self, message):
        """^^"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Необходимо указать название файла.</b>")
            return

        await utils.answer(message, self.strings("loading_file"))
        await self._send_file_by_message_text(message, channel_username="Heta_Modules", search_text=args)

    async def _send_file_by_message_text(self, message, channel_username, search_text):
        try:
            channel_entity = await message.client.get_entity(channel_username)
            offset_id = 0

            while True:
                messages = await message.client.get_messages(channel_entity, limit=100, offset_id=offset_id)
                if not messages:
                    break

                for msg in messages:
                    if msg.file and search_text.lower() in (msg.message or "").lower():
                        await msg.forward_to(message.peer_id)
                        await message.delete()
                        return

                offset_id = messages[-1].id

            await utils.answer(message, self.strings("error_loading"))

        except Exception as e:
            logger.error(f"Error fetching file from channel {channel_username}: {e}")
            await utils.answer(message, self.strings("error_loading"))

