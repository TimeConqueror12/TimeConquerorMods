# meta developer: @hikkagpt | @minovayIa_a - @DeuteriumModules (redact)

# В чужих кодах роешься, пупсик?
# Честно говоря, это пиздец полный а не код, оригинальный модуль был ещё хуже. Без обид)

import json
import aiohttp
import requests
import re
import os
import base64
from time import sleep
from bs4 import BeautifulSoup
from telethon import events
from telethon.tl.custom import Message
from .. import loader, utils

available_models = {
    "1": "o3-mini",
    "2": "o1-preview",
    "3": "o1-Mini",
    "4": "gpt-4o",
    "5": "gpt-4o-mini",
    "6": "gpt4-turbo",
    "7": "gpt-3.5-turbo",
    "8": "gpt-4",
    "9": "deepseek-v3",
    "10": "deepseek-r1",
    "11": "gemini",
    "12": "gemini-1.5 Pro",
    "13": "gemini-flash",
    "14": "llama-3.1",
    "15": "llama-2",
    "16": "claude-3-haiku",
    "17": "claude-3.5-sonnet",
    "18": "bard",
    "19": "qwen",
    "20": "t-pro",
    "21": "t-lite"
}

@loader.tds
class AIModule(loader.Module):
    """
🧠 Модуль Zetta
🌒 Version: 8.3 | Andrew fork  
"""
    strings = {"name": "Zetta - AI models"}

    def __init__(self):
        super().__init__()
        self.default_model = "gpt4-turbo"
        self.active_chats = {}
        self.chat_history = {}
        self.chat_archive = {}
        self.role = {}
        self.response_mode = {}
        self.edit_promt = "off"
        self.instructions = self.get_instructions()
        self.error_instructions = self.get_error_instructions()
        self.module_instructions = self.get_module_instruction()
        self.double_instructions = self.get_double_instruction()
        self.allmodule_instruction = self.get_allmodule_instruction()
        self.module_instruction2 = self.get_module_instruction2()
        self.module_instruction3 = self.get_module_instruction3()
        self.allmodule_instruction2 = self.get_allmodule_instruction2()
        self.metod = "on"
        self.provider = 'zetta'
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        self.handle_voice_message = self.handle_voice_message
        self.humanmode = 'off'

    @loader.unrestricted
    async def aisupcmd(self, message):
        """
        Использование: .aisup <запрос>/<реплай>
        """
        await self.process_request(message, self.instructions, "sup")

    @loader.unrestricted
    async def aierrorcmd(self, message):
        """
        Использование: .aierror <запрос>/<реплай>
        """
        await self.process_request(message, self.error_instructions, "error")

    def get_instructions(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/data-set1.txt')

    def get_error_instructions(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/error_set.txt')

    def get_module_instruction(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/module_set.txt')

    def get_double_instruction(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/data-set2.txt')

    def get_allmodule_instruction(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/data-set3.txt')

    def get_allmodule_instruction2(self):
        return self.fetch_data("https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/data-set4.txt")

    def get_module_instruction2(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/module_set2.txt')

    def get_module_instruction3(self):
        return self.fetch_data('https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/module_set3.txt')

    def fetch_data(self, url):
        response = requests.get(url)
        return response.text

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.active_chats = self.db.get("AIModule", "active_chats", {})
        self.chat_history = self.db.get("AIModule", "chat_history", {})
        self.chat_archive = self.db.get("AIModule", "chat_archive", {})
        self.role = self.db.get("AIModule", "role", {})
        self.response_mode = self.db.get("AIModule", "response_mode", {})

    async def handle_voice_message(self, message: Message):
        try:
            file_path = await self.client.download_media(message.voice)
            audio_path = "temp_audio.wav"
            audio = AudioSegment.from_ogg(file_path)
            audio.export(audio_path, format="wav")

            voice = await message.edit("Слушаю...🎙")
            recognized_text = recognize_audio(audio_path)

            if recognized_text:
                return recognized_text
            else:
                await message.edit("Не удалось распознать голосовое сообщение.")

            os.remove(audio_path)
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}")

    @loader.unrestricted
    async def modelcmd(self, message):
        """
        Использование: .model <номер> или `.model list` для вывода списка.
        """
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("🤔 <b>Укажите номер модели или list для просмотра списка.</b>")
            return

        if args == "list":
            model_list = "\n".join([f"<b>{k}.</b> {v}" for k, v in available_models.items()])
            await message.edit(f"📝 <b>Доступные модели:</b>\n{model_list}")
            return

        if args not in available_models:
            await message.edit("🚫 <b>Неверный номер модели.</b>")
            return

        self.default_model = available_models[args]
        await message.edit(f"✅ <b>Модель изменена на:</b> {self.default_model}")

    @loader.unrestricted
    async def chatcmd(self, message):
        """
        Включает/выключает режим чата.
        """
        chat_id = str(message.chat_id)
        if chat_id in self.active_chats:
            self.active_chats.pop(chat_id, None)
            self.db.set("AIModule", "active_chats", self.active_chats)

            if chat_id in self.chat_history:
                self.chat_archive[chat_id] = self.chat_history[chat_id]
                self.chat_history.pop(chat_id, None)
                self.db.set("AIModule", "chat_history", self.chat_history)
                self.db.set("AIModule", "chat_archive", self.chat_archive)
                await message.edit("📴 <b>Режим чата выключен. История архивирована.</b>")
            else:
                await message.edit("📴 <b>Режим чата выключен.</b>")
        else:
            self.active_chats[chat_id] = True
            self.db.set("AIModule", "active_chats", self.active_chats)

            if chat_id in self.chat_archive:
                self.chat_history[chat_id] = self.chat_archive[chat_id]
                self.chat_archive.pop(chat_id, None)
                self.db.set("AIModule", "chat_history", self.chat_history)
                self.db.set("AIModule", "chat_archive", self.chat_archive)
                await message.edit("💬 <b>Режим чата включен. История загружена.</b>")
            else:
                await message.edit("💬 <b>Режим чата включен.</b>")

    async def send_request_to_api(self, message, instructions, request_text, model="gpt-4o-mini"):
        """Отправляет запрос к API и возвращает ответ."""
        api_url = "http://109.172.94.236:5001/Zetta/v1/models" if self.provider == "zetta" else "https://api.vysssotsky.ru/"
        
        if self.provider == 'devj':
            # Формируем payload для запроса к devj API
            payload = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": f"{instructions}\nЗапрос пользователя: {request_text}"}],
                "max_tokens": 10048,
                "temperature": 0.7,
                "top_p": 1,
            }

            print(f"Отправляем запрос на {api_url} с данными: {payload}")  # Отладочная информация

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"https://api.vysssotsky.ru/v1/chat/completions", 
                                           headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                                           data=json.dumps(payload)) as response:
                        if response.status == 200:
                            data = await response.json()
                            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "Ответ не получен.")
                            return f"<blockquote>{answer}</blockquote>"
                        else:
                            error_message = await response.text()  # Получаем текст ошибки
                            await message.edit(f"⚠️ Ошибка при запросе к API: {error_message}")
            except Exception as e:
                await message.edit(f"⚠️ Ошибка при запросе к API: {e}")

        else:
            payload = {
                "model": self.default_model,
                "request": {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{instructions}\nНе используй HTML и форматирование текста. Также помни, что тебе нужно сохранить ответ предыдущей части модуля, если ты не знаешь ответа. И передать его дальше.\nЗапрос пользователя: {request_text}"
                        }
                    ]
                }
            }

            print(f"Отправляем запрос на {api_url} с данными: {payload}")  # Отладочная информация

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()

                        answer = data.get("answer", "🚫 Ответ не получен.").strip()
                        decoded_answer = base64.b64decode(answer).decode('utf-8')
                        return decoded_answer

            except aiohttp.ClientError as e:
                await message.edit(f"⚠️ Ошибка при запросе к API: {e}\n\n💡 Попробуйте поменять модель или проверить код модуля.")
                return None

    async def allmodule(self, answer, message, request_text):
        rewrite2 = self.get_allmodule_instruction()
        await message.edit("<b>🎭Цепочка размышлений модели в процессе:\n🟢Первая модель приняла решение\n🟢Вторая модель приняла решение.\n💭Третья модель думает...</b>\n\nПочему так долго: каждая модель имеет свой дата сет. И сверяет ответ предыдущей модели с своими знаниями.")
        answer = await self.send_request_to_api(message, rewrite2, f"Запрос пользователя: {request_text}\nОтвет второй части модуля:{answer}")
        if answer:
            await self.allmodule2(answer, message, request_text)

    async def modulecreating(self, answer, message, request_text):
        rewrite = self.get_module_instruction2()
        await message.edit("<b>🎭Создается модуль:\n🟢Создание кода\n💭Тестирование...</b>\n\nЗаметка: чем лучше вы расспишите задачу для модели - тем лучше она создаст модуль. ")
        answer = await self.send_request_to_api(message, rewrite, f"User request: {request_text}\nAnswer to the first part of the module:{answer}")
        if answer:
            await self.modulecreating2(answer, message, request_text)

    async def allmodule2(self, answer, message, request_text):
        rewrite3 = self.get_allmodule_instruction2()  # Используем новый датасет
        await message.edit("<b>🎭Цепочка размышлений модели в процессе:\n🟢Первая модель приняла решение\n🟢Вторая модель приняла решение.\n🟢Третья модель приняла решение\n💭Четвертая модель думает...</b>\n\nПочему так долго: каждая модель имеет свой дата сет. И сверяет ответ предыдущей модели с своими знаниями.")
        answer = await self.send_request_to_api(message, rewrite3, f"Запрос пользователя: {request_text}\nОтвет третьей части модуля:{answer}")
        if answer:
            formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka</b>:\n{answer}"
            await message.edit(formatted_answer)

    async def modulecreating2(self, answer, message, request_text):
        rewrite = self.get_module_instruction3()
        await message.edit("<b>🎭Создается модуль:\n🟢Создание кода\n🟢Протестировано\n💭Проверка на безопастность и финальное тестирование...</b>\n\nЕще заметка: Лучше проверяйте что написала нейросеть, перед тем как использовать модуль.")
        answer = await self.send_request_to_api(message, rewrite, f"User request: {request_text}\nAnswer to the first part of the module:{answer}")
        if answer:
            try:
                if len(answer) > 4096:
                    await message.edit("⚠️ Код модуля слишком большой для отправки в сообщении. Был выслан просто файл.")
                    await self.save_and_send_code(answer, message)
                else:
                    await message.edit(f"<b>💡 Ответ AI-помощника по Hikka | Креатор модулей</b>:\n{answer}")
                    await self.save_and_send_code(answer, message)
            except Exception as e:
                if "Message was too long" in str(e):
                    await message.edit("⚠️ Код модуля слишком большой для отправки в сообщении. Отправляю файл...")
                    await self.save_and_send_code(answer, message)
                else:
                    await message.edit(f"⚠️ Ошибка: {e}")

    async def rewrite_process(self, answer, message, request_text):
        rewrite = self.get_double_instruction()
        await message.edit("<b>🎭Цепочка размышлений модели в процессе:\n🟢Первая модель приняла решение\n💭Вторая модель думает...</b>\n\nПочему так долго: каждая модель имеет свой дата сет. И сверяет ответ предыдущей модели с своими знаниями.")
        answer = await self.send_request_to_api(message, rewrite, f"Запрос пользователя: {request_text}\nОтвет первой части модуля:{answer}")
        if answer:
            await self.allmodule(answer, message, request_text)

    @loader.unrestricted
    async def apiswitchcmd(self, message):
        """
        Использование: .apiswitch <провайдер>
        доступные: zetta и devj.
        """
        args = utils.get_args_raw(message)
        if args:
            provider = args.lower() 
            if provider in ("zetta", "devj"):
                self.provider = provider
                await message.edit(f"✅ Провайдер API изменен на {provider}")
            else:
                await message.edit("🚫 Недопустимый провайдер API. Доступные: zetta, devj")
        else:
            await message.edit("🤔 Укажите провайдер API: zetta или devj")

    @loader.unrestricted
    async def aicreatecmd(self, message):
        """
        Использование: .aicreate <запрос>/<реплай>
        """
        await self.process_request(message, self.module_instructions, "create")

    @loader.unrestricted
    async def ultramodecmd(self, message):
        """
        Использование: `.ultramode <on/off>`
        """
        args = utils.get_args_raw(message)
        if args:
            metod = args.lower()
            if metod in ("on", "off"):
                self.metod = metod
                await message.edit(f"📚 Качественный ответ {'включен' if metod == 'on' else 'выключен'}. Скорость ответа aisup {'меньше' if metod == 'on' else 'быстрее'}.")
            else:
                await message.edit("🚫 Неправильные аргументы. Доступные: on, off")
        else:
            await message.edit("🤔 Укажите аргументы: on или off")

    async def save_and_send_code(self, answer, message):
        """Сохраняет код в файл, отправляет его и удаляет."""
        try:
            code_start = answer.find("`python") + len("`python")
            code_end = answer.find("```", code_start)
            code = answer[code_start:code_end].strip()
    
            with open("AI-module.py", "w") as f:
                f.write(code)
    
            await message.client.send_file(
                message.chat_id,
                "AI-module.py",
                caption="<b>💫Ваш готовый модуль</b>",
            )
    
            os.remove("AI-module.py")
    
        except (TypeError, IndexError) as e:
            await message.reply(f"Ошибка при извлечении кода: {e}")
        except Exception as e:  
            await message.reply(f"Ошибка при обработке кода: {e}")

    async def process_request(self, message, instructions, command):
        """
        Обрабатывает запрос к API модели ИИ.
        """
        if message.voice:
            request_text = await self.handle_voice_message(message)
        else:
            reply = await message.get_reply_message()
            args = utils.get_args_raw(message)

            if reply:
                request_text = reply.raw_text
            elif args:
                request_text = args
            else:
                await message.edit("🤔 Введите запрос или ответьте на сообщение.")
                return

        try:
            await message.edit("<b>🤔 Думаю...</b>")
            answer = await self.send_request_to_api(message, instructions, request_text)
            if answer:
                if command == "error":
                    formatted_answer = f"💡<b> Ответ AI-помощника по Hikka | Спец. по ошибкам</b>:\n{answer}"
                    await message.edit(formatted_answer)
                elif command == "sup":
                    if self.metod == "on":
                        await message.edit("<b>💬Размышления моделей начались..</b>")
                        await self.rewrite_process(answer, message, request_text)
                    else:
                        formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka | Режим быстрого ответа</b>:\n{answer}\n\n❕В этом режиме модель ограничена знаниями встроенных модулей и базовой документации hikka"
                        await message.edit(formatted_answer)
                elif command == "create":
                    await self.modulecreating(answer, message, request_text)
                elif command == 'rewrite':
                    formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka</b>:\n{answer}"
                    await message.edit(formatted_answer)
                else:
                    formatted_answer = answer
                    await message.edit(formatted_answer)

        except Exception as e:
            await message.edit(f"⚠️ Ошибка: {e}")
    
    @loader.unrestricted
    async def clearcmd(self, message):
        """
        Сбрасывает историю диалога.
        """
        chat_id = str(message.chat_id)
        if chat_id in self.chat_history or chat_id in self.chat_archive:
            self.chat_history.pop(chat_id, None)
            self.chat_archive.pop(chat_id, None)
            self.db.set("AIModule", "chat_history", self.chat_history)
            self.db.set("AIModule", "chat_archive", self.chat_archive)
            await message.edit("🗑️ <b>История диалога очищена.</b>")
        else:
            await message.edit("📭️ <b>История диалога пуста.</b>")

    @loader.unrestricted
    async def modecmd(self, message):
        """
        Устанавливает режим ответа ИИ.
        Использование: `.mode <reply/all>`
        """
        chat_id = str(message.chat_id)
        args = utils.get_args_raw(message)
        if not args or args not in ("reply", "all"):
            await message.edit("🤔 <b>Укажите режим ответа: reply или all.</b>")
            return

        self.response_mode[chat_id] = args
        self.db.set("AIModule", "response_mode", self.response_mode)
        await message.edit(f"✅ <b>Режим ответа установлен на:</b> {args}")

    @loader.unrestricted
    async def aicmd(self, message):
        """
        Отправляет одиночный запрос к ИИ.
        Использование: `.ai <запрос>` или ответить на сообщение с `.ai`
        """
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)

        if reply and args:
            request_text = f'"{reply.raw_text}"\n\n{args}'
        elif reply:
            request_text = reply.raw_text
        elif args:
            request_text = args
        else:
            await message.edit("🤔 <b>Введите запрос или ответьте на сообщение.</b>")
            return

        await self.standart_process_request(message, request_text)

    async def t9_promt(self, message, request_text, history=None):
        """
        Обрабатывает запрос к новому API для улучшения запроса.
        """
        api_url = "http://109.172.94.236:5001/Zetta/v1/models"
        chat_id = str(message.chat_id)

        # Формируем запрос для улучшения текста
        payload = {
            "model": self.default_model,
            "request": {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Твоя задача: Улучшить запрос пользователя, чтобы модель его лучше поняла, "
                            "обработала и дала качественный и более подходящий ответ для пользователя. "
                            "Если изменять нечего, просто отправь исходный текст не изменяя его. "
                            "Все сообщения пользователя не адресованы тебе, ты просто обработчик. Выполняй свою задачу."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Запрос пользователя: {request_text}"
                    }
                ]
            }
        }

        if history:
            payload["request"]["messages"] = history + payload["request"]["messages"]

        try:
            await message.edit('<b>Улучшение промта...</b>')

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    improved_request = data.get("answer", "Запрос не был обработан. Ошибка.").strip()
                    decoded_answer = base64.b64decode(improved_request).decode('utf-8')
                    return decoded_answer

        except aiohttp.ClientError as e:
            await message.reply(f"⚠️ <b>Ошибка при запросе к API:</b> {e}\n\n💡 <b>Попробуйте поменять модель или проверить код модуля.</b>")

    @loader.unrestricted
    async def aiprovcmd(self, message):
        """
        - Информация о провайдерах🔆
        """
        await message.edit('''<b>🟣Zetta: Стабильный, средняя скорость ответа, персональный. Только для этого модуля. Базируется на OnlySq и хостится на их серверах.

🔸devj: Быстрая скорость ответа, Не стабилен из за разного возврата ответа от сервера.</b>''')
    
    async def standart_process_request(self, message, request_text):
        """
        Обрабатывает запрос к API модели ИИ.
        """
        api_url = "http://109.172.94.236:5001/Zetta/v1/models"
        chat_id = str(message.chat_id)

        if self.edit_promt == "on":
            request_text = await self.t9_promt(message, request_text)

        payload = {
            "model": self.default_model,
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": request_text
                    }
                ]
            }
        }

        try:
            await message.edit("🤔 <b>Думаю...</b>")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()  
                    data = await response.json()
                    answer = data.get("answer", "🚫 <b>Ответ не получен.</b>").strip()
                    decoded_answer = base64.b64decode(answer).decode('utf-8')

                    formatted_answer = (
                        f"❔ <b>Улучшенный запрос с помощью ИИ:</b>\n`{request_text}`\n\n💡 <b>Ответ модели {self.default_model}:</b>\n{decoded_answer}"
                        if self.edit_promt == "on" else
                        f"❔ <b>Запрос:</b>\n`{request_text}`\n\n💡 <b>Ответ модели {self.default_model}:</b>\n{decoded_answer}"
                    )

                    await message.edit(formatted_answer)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ <b>Ошибка при запросе к API:</b> {e}\n\n💡 <b>Попробуйте поменять модель или проверить код модуля.</b>")

    @loader.unrestricted
    async def humanmodecmd(self, message):
        """
        <on/off> - используется для улучшения промта
        """
        args = utils.get_args_raw(message)
        if args:
            humanmode = args.lower()
            if humanmode in ("on", "off"):
                self.humanmode = humanmode
                await message.edit(f"💫 <b>Отображение 'Ответ модели ...' {'отключено' if humanmode == 'on' else 'включено'} в режиме чата.</b>")
            else:
                await message.edit("🚫 Неправильные аргументы. Доступные: on, off")
        else:
            await message.edit("🤔 Укажите аргументы: on или off")

    @loader.unrestricted
    async def superpromtcmd(self, message):
        """
        <on/off> - используется для улучшения промта
        """
        args = utils.get_args_raw(message)
        if args:
            edit_promt = args.lower()
            if edit_promt in ("on", "off"):
                self.edit_promt = edit_promt
                await message.edit(f"💫 <b>Улучшение вашего промта {'включено' if edit_promt == 'on' else 'выключено'}</b>")
            else:
                await message.edit("🚫 Неправильные аргументы. Доступные: on, off")
        else:
            await message.edit("🤔 Укажите аргументы: on или off")

    @loader.unrestricted
    async def watcher(self, message):
        """
        Следит за сообщениями и отвечает, если активен режим чата.
        """
        chat_id = str(message.chat_id)
        if self.active_chats.get(chat_id):
            if self.response_mode.get(chat_id, "all") == "reply" and \
               not (message.is_reply and await self.is_reply_to_bot(message)):
                return

            request_text = await self.handle_voice_message(message) if message.voice else message.text.strip()
            user_name = await self.get_user_name(message)
            await self.respond_to_message(message, user_name, request_text)

    async def is_reply_to_bot(self, message):
        """
        Проверяет, является ли сообщение ответом на сообщение бота.
        """
        if message.is_reply:
            reply_to_message = await message.get_reply_message()
            return reply_to_message and reply_to_message.sender_id == (await self.client.get_me()).id
        return False

    async def get_user_name(self, message):
        """
        Возвращает имя пользователя из сообщения.
        """
        if message.sender:
            user = await self.client.get_entity(message.sender_id)
            return user.first_name or user.username
        return "Аноним"  

    async def respond_to_message(self, message, user_name, question):  
        """
        Обрабатывает вопрос и отправляет ответ с учетом истории.
        """
        chat_id = str(message.chat_id)

        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = []

        self.chat_history[chat_id].append({
            "role": "user",
            "content": f"{user_name} написал: {question}"
        })

        if len(self.chat_history[chat_id]) > 1000:
            self.chat_history[chat_id] = self.chat_history[chat_id][-1000:]

        if self.edit_promt == "on":
            question = await self.t9_promt(message, question, self.chat_history[chat_id])
        
        self.chat_history[chat_id][-1]["content"] = f"{user_name} написал: {question}"

        api_url = "http://109.172.94.236:5001/Zetta/v1/models"
        payload = {
            "model": self.default_model,
            "request": {
                "messages": [
                    {"role": "system", "content": self.role.get(chat_id, "")}
                ] + self.chat_history[chat_id]
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()  
                    data = await response.json()
                    answer = data.get("answer", "🚫 <b>Ответ не получен.</b>").strip()
                    decoded_answer = base64.b64decode(answer).decode('utf-8')

                    self.chat_history[chat_id].append({
                        "role": "assistant",
                        "content": decoded_answer
                    })

                    self.db.set("AIModule", "chat_history", self.chat_history)

                    await message.reply(f"<b>Ответ модели {self.default_model}:</b>\n{decoded_answer}" if self.humanmode == 'off' else decoded_answer)

        except aiohttp.ClientError as e:
            await message.reply(f"⚠️ <b>Ошибка при запросе к API:</b> {e}\n\n💡 <b>Попробуйте поменять модель или проверить код модуля.</b>")

    @loader.unrestricted
    async def rewritecmd(self, message):
        """
        <инструкция для исправления>
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Пожалуйста, укажите инструкцию для переписывания.</b>")
            return

        if not message.is_reply:
            await utils.answer(message, "<b>Пожалуйста, ответьте на сообщение, которое нужно переписать.</b>")
            return

        reply_message = await message.get_reply_message()
        original_text = reply_message.text

        if not original_text:
            await utils.answer(message, "<b>Не найден текст для переписывания.</b>")
            return

        instruction = args
        api_url = "http://109.172.94.236:5001/Zetta/v1/models"
        payload = {
            "model": self.default_model,
            "request": {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты — помощник для переписывания текста. "
                            "Твоя задача — переписывать текст по указанной пользователем инструкции, "
                            "отвечать четко и по делу, не выходя за рамки своей задачи. "
                            "Не используй Latex или особое форматирование, сохраняй текст простым и доступным."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"{instruction}: {original_text}"
                    }
                ]
            }
        }

        try:
            await message.edit('<b>💭Переписываю..</b>')

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()  
                    data = await response.json()
                    rewritten_text = data.get("answer", "🚫 <b>Ответ не получен.</b>").strip()
                    decoded_answer = base64.b64decode(rewritten_text).decode('utf-8')
                    formatted_answer = f"✏️ <b>Переписанный текст моделью {self.default_model}:</b>\n{decoded_answer}"

                    await message.edit(formatted_answer)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ <b>Ошибка при запросе к API:</b> {e}")
        except Exception as e:
            await message.edit(f"⚠️ <b>Произошла ошибка:</b> {e}")
