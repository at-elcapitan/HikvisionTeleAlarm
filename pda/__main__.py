import os
import json
import asyncio

import hikvisionapi as hikv
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import types

# Globals
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = AsyncTeleBot(TOKEN)


def main():
    hikv.AsyncClient()


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    with open('files/allowed_chats.json', "r") as f:
        data = json.load(f)

    if message.chat.id in data:
        await bot.reply_to(message, "Если вы видите данное сообщение, значит чат находится в вайтлисте.")
        return
    
    await bot.reply_to(message, f"Фатальная ошибка: данный чат не добавлен в вайтлист.\nИдентефикатор чата: `{message.chat.id}`\nНапишите @takhiga для добавления в вайтлист.", parse_mode="Markdown")


if __name__ == "__main__":
    print("pda-03072023")
    if not os.path.exists('files'):
        os.mkdir('files')

    if not os.path.isfile('files/allowed_chats.json'):
        def_config = []
        with open('files/allowed_chats.json', 'w') as f:
            f.seek(0)
            json.dump(def_config, f, indent=4, ensure_ascii=False)
            f.truncate()

    asyncio.run(bot.polling())
    main()