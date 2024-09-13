#meta developer: @anskilll
import aiohttp
from .. import loader, utils

def register(cb):
    cb(URLShortenerMod())

class URLShortenerMod(loader.Module):
    """Сократитель ссылок"""
    strings = {'name': 'URLShortener'}

    async def lgtcmd(self, message):
        """Сократить ссылку с помощью сервиса tinyurl.com"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("Нет аргументов.")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://tinyurl.com/api-create.php?url={args}") as response:
                if response.status == 200:
                    link = await response.text()
                    await message.edit(f"Сокращённая ссылка:\n> {link}")
                else:
                    await message.edit("Ошибка при сокращении ссылки.")