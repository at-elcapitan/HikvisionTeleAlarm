import os
import io
import json
import asyncio
import threading
from datetime import datetime

import hikvisionapi as hikv
from dotenv import load_dotenv
from telebot import TeleBot
from telebot import types

# Globals
load_dotenv()
TOKEN = os.getenv('TOKEN')
HOST = os.getenv('HOST')
LOGIN = os.getenv('LOGIN')
PASSWD = os.getenv('PASSWD')
bot = TeleBot(TOKEN)


class EnvironmentError(Exception):
    def __init__(self) -> None:
        super().__init__(f'Can`t import global variables. Maybe .env file corrupted or filled incorrectly.')


async def main() -> None:
    try:
        aclient = hikv.AsyncClient(HOST, LOGIN, PASSWD)
    except:
        return
    
    last = datetime.now()
    
    async for event in aclient.Event.notification.alertStream(method='get', type='stream', timeout=None):
        if event['EventNotificationAlert']['eventDescription'] == 'Motion alarm':
            print('event')
            channel = event['EventNotificationAlert']['dynChannelID']

            if (datetime.now() - last).total_seconds() < 15:
                continue
            
            last = datetime.now()
            with open('files/channels.json', 'r') as f:
                data = json.load(f)

            cam_name = data[channel]
            time = str(datetime.now())[:-7]

            '''with open('screen.jpg', 'wb') as f:
                async for chunk in aclient.Streaming.channels[int(channel)*100].picture(method='get', type='opaque_data'):
                    if chunk:
                        f.write(chunk)
                
                photo = f'''

            with open('files/allowed_chats.json', "r") as f:
                chats = json.load(f)

            '''for chat in chats:
                bot.send_photo(chat, photo, f"SYSTEM ALERT\nОбнаружено движение на камере: {cam_name}\nВремя: {time}")'''
            
            for chat in chats:
                bot.send_message(chat, f"SYSTEM ALERT\nОбнаружено движение на камере: {cam_name}\nВремя: {time}")

        await asyncio.sleep(1)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message) -> None:
    with open('files/allowed_chats.json', "r") as f:
        data = json.load(f)

    if message.chat.id in data:
        bot.reply_to(message, "Если вы видите данное сообщение, значит чат находится в вайтлисте.")
        return
    
    bot.reply_to(message, f"Данный чат не добавлен в вайтлист - фатальная ошибка.\nИдентефикатор чата: `{message.chat.id}`\nНапишите @takhiga для добавления в вайтлист.", parse_mode="Markdown")


@bot.message_handler(commands=['addchat'])
def add_chat(message) -> None:
    if message.from_user.id in [1202182074]:
        msg = bot.reply_to(message, f"Запрос авторизирован. Добро пожаловать в систему, @{message.from_user.username}\n\nПровожу регистрацию чата...")

        with open('files/allowed_chats.json', 'r+') as f:
            data = json.load(f)

            if message.chat.id in data:
                bot.edit_message_text(f"Запрос авторизирован. Добро пожаловать в систему, @{message.from_user.username}\n\nОшибка: чат уже находится в вайтлисте.", message.chat.id, msg.id)
                return
            
            data.append(message.chat.id)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        
        bot.edit_message_text(f"Запрос авторизирован. Добро пожаловать в систему, @{message.from_user.username}\n\nПровожу регистрацию чата... Выполнено!", message.chat.id, msg.id)
        return
    
    bot.reply_to(message, "Фатальная ошибка авторизации.")


if __name__ == "__main__":
    print("pda-v0.1.0 Starting...")
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
    thread = threading.Thread(target=bot.polling)
    thread_main = threading.Thread(target=asyncio.run, args=(main(),))
    print("Starting...")
    thread_main.start()
    thread.start()
    print("Started.")
    thread_main.join()
    thread.join()
