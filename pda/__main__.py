import os
import io
import json
import asyncio
import threading
from datetime import datetime

import hikvisionapi as hikv
from dotenv import load_dotenv
from telebot import TeleBot
#from telebot import types

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
            channel = event['EventNotificationAlert']['dynChannelID']

            if (datetime.now() - last).total_seconds() < 15:
                continue
            
            last = datetime.now()
            with open('files/camera.json', 'r') as f:
                data = json.load(f)
            
            try:
                cam_name = data[channel]
            except:
                cam_name = "Unknown"

            time = str(datetime.now())[:-7]

            with open('files/chats.json', "r") as f:
                chats = json.load(f)
            
            for chat in chats:
                bot.send_message(chat, f"SYSTEM ALERT\nMotion registered on camera `{cam_name}`\nDateTime: {time}", parse_mode='Markdown')

        await asyncio.sleep(1)


@bot.message_handler(commands=['init'])
def add_chat(message) -> None:
    with open('files/admins.json', "r") as f:
        data = json.load(f)

    if message.from_user.id in data:
        msg = bot.reply_to(message, f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering a chat...")

        with open('files/chats.json', 'r+') as f:
            data = json.load(f)

            if message.chat.id in data:
                bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nError: chat is already in the whitelist", message.chat.id, msg.id)
                return
            
            data.append(message.chat.id)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        
        bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\nRegistering a chat... Done!", message.chat.id, msg.id)
        return
    
    bot.reply_to(message, "Authorization failed.")


@bot.message_handler(commands=['getuserid'])
def get_id(message) -> None:
    bot.reply_to(message, f"Your id is `{message.from_user.id}`", parse_mode='Markdown')


@bot.message_handler(commands=['addadmin'])
def add_admin(message) -> None:
    with open('files/admins.json', "r") as f:
        data = json.load(f)

    admin_id = message.text.split()[1:]

    if message.from_user.id in data:
        msg = bot.reply_to(message, f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering new admin...")

        with open('files/admins.json', 'r+') as f:
            data = json.load(f)

            try:
                admin_id = int(admin_id)
            except:
                bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nError while converting adminID to integer.", message.chat.id, msg.id)
                return

            if admin_id in data:
                bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nError: admin is already registered.", message.chat.id, msg.id)
                return
            
            data.append(message.chat.id)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
        
        bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering admin... Done!", message.chat.id, msg.id)
        return
    
    bot.reply_to(message, "Authorization failed.")


if __name__ == "__main__":
    print("pda-v0.2.0 Starting...")
    if TOKEN is None or PASSWD is None or HOST is None or LOGIN is None:
        raise EnvironmentError

    if not os.path.exists('files'):
        os.mkdir('files')

    if not os.path.isfile('files/chats.json'):
        def_config = []
        with open('files/chats.json', 'w') as f:
            f.seek(0)
            json.dump(def_config, f, indent=4, ensure_ascii=False)
            f.truncate()

    if not os.path.isfile('files/camera.json'):
        def_config = {}
        with open('files/camera.json', 'w') as f:
            f.seek(0)
            json.dump(def_config, f, indent=4, ensure_ascii=False)
            f.truncate()

    if not os.path.isfile('files/admins.json'):
        def_config = []
        with open('files/admins.json', 'w') as f:
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
