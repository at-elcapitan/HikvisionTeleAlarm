import os
import json
import asyncio
import threading

import hikvisionapi as hikv
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import types

# Globals
load_dotenv()
TOKEN = os.getenv('TOKEN')
HOST = os.getenv('HOST')
LOGIN = os.getenv('LOGIN')
PASSWD = os.getenv('PASSWD')
bot = AsyncTeleBot(TOKEN)


class EnvironmentError(Exception):
    def __init__(self) -> None:
        super().__init__(f'Can`t import global variables. Maybe .env file corrupted or filled incorrectly.')


async def main():
    aclient = hikv.AsyncClient("http://10.10.10.2:80", "150", "150-150A", timeout=5)

    with open('screen.jpg', 'wb') as f:
        async for chunk in aclient.Streaming.channels[102].picture(method='get', type='opaque_data'):
            if chunk:
                f.write(chunk)


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message) -> None:
    with open('files/allowed_chats.json', "r") as f:
        data = json.load(f)

    if message.chat.id in data:
        await bot.reply_to(message, "Если вы видите данное сообщение, значит чат находится в вайтлисте.")
        return
    
    await bot.reply_to(message, f"Фатальная ошибка: данный чат не добавлен в вайтлист.\nИдентефикатор чата: `{message.chat.id}`\nНапишите @takhiga для добавления в вайтлист.", parse_mode="Markdown")


@bot.message_handler(commands=['addchat'])
async def add_chat(message) -> None:
    if message.from_user.id in [1202182074]:
        await bot.reply_to(message, f"Запрос авторизирован. Добро пожаловать в систему, @{message.from_user.username}\n\nПровожу регистрацию чата...")

        with open('files/allowed_chats.json', 'r+') as f:
            data = json.load(f)

            if message.chat.id in data:
                await bot.send_message(message.chat.id, "Ошибка: чат уже находится в вайтлисте.")
                return
            
            data.append(message.chat.id)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        
        await bot.send_message(message.chat.id, "Выполнено.")
        return
    
    await bot.reply_to(message, "Фатальная ошибка авторизации.")


if __name__ == "__main__":
    print("pda-030720232312 Starting...")
    if TOKEN is None or PASSWD is None or HOST is None or LOGIN is None:
        raise EnvironmentError

    if not os.path.exists('files'):
        os.mkdir('files')

    if not os.path.isfile('files/allowed_chats.json'):
        def_config = []
        with open('files/allowed_chats.json', 'w') as f:
            f.seek(0)
            json.dump(def_config, f, indent=4, ensure_ascii=False)
            f.truncate()

    print("Creating threads")
    thread = threading.Thread(target=asyncio.run, args=(bot.polling(),))
    thread_main = threading.Thread(target=asyncio.run, args=(main(),))
    print("Starting...")
    thread_main.start()
    thread.start()
    print("Started.")
    thread_main.join()
    thread.join()