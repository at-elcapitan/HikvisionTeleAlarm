import os
import json
import asyncio
from datetime import datetime

import hikvisionapi as hikv
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import prettytable as pt

# Globals
load_dotenv()
TOKEN = os.getenv('TOKEN')
HOST = os.getenv('HOST')
LOGIN = os.getenv('LOGIN')
PASSWD = os.getenv('PASSWD')
TIMEOUT = os.getenv('TIMEOUT')
bot = AsyncTeleBot(TOKEN)
aclient = None


class EnvironmentError(Exception):
    def __init__(self) -> None:
        super().__init__(f'Can`t import global variables. Maybe .env file corrupted or filled incorrectly.')


class ReadError(Exception):
    def __init__(self, filename) -> None:
        super().__init__(f"File {filename} data read error.")


async def main() -> None:
    global aclient

    try:
        aclient = hikv.AsyncClient(HOST, LOGIN, PASSWD)
    except:
        return

    with open('files/camera.json', 'r') as f:
        time = json.load(f)

    for x in time:
        time[x] = datetime.now()

    async for event in aclient.Event.notification.alertStream(method='get', type='stream', timeout=10):
        if not event['EventNotificationAlert']['eventDescription'] == 'Motion alarm':
            await asyncio.sleep(1)
            continue

        channel = event['EventNotificationAlert']['dynChannelID']

        with open('files/camera.json', 'r') as f:
            data = json.load(f)
        
        try:
            cam_name = data[channel][0]
            cam_enable = data[channel][1]
        except:
            raise ReadError('camera.json')

        if not cam_enable:
            return

        if (datetime.now() - time[channel]).total_seconds() < int(TIMEOUT):
            continue
        
        time[channel] = datetime.now()

        time_str = str(datetime.now())[:-7]

        with open('files/chats.json', "r") as f:
            chats = json.load(f)
        
        for chat in chats:
            await bot.send_message(chat, f"SYSTEM ALERT\nMotion registered on camera `{cam_name}`\nDateTime: {time_str}", parse_mode='Markdown')

@bot.message_handler(commands=['list'])
async def camera_list(message):
    with open('files/camera.json', 'r') as f:
        data = json.load(f)

    table = pt.PrettyTable(['ID', 'State', 'Name'])
    table.vertical_char = "│"
    table.horizontal_char = "─"
    table.junction_char = "┼"
    table.left_junction_char = "├"
    table.right_junction_char = "┤"
    table.bottom_junction_char = "┴"
    table.bottom_left_junction_char = "└"
    table.bottom_right_junction_char = "┘"
    table.top_junction_char = "┬"
    table.top_right_junction_char = "┐"
    table.top_left_junction_char = "┌"
    table.right_padding_width = 2
    table.left_padding_width = 2
    table.align['ID'] = 'r'
    table.align['State'] = 'l'
    table.align['Name'] = 'l'

    for id, camera in data.items():
        table.add_row([id, "Enabled" if camera[1] else "Disabled", camera[0]])

    await bot.reply_to(message, f'<pre>{table}</pre>\n\nIf the table is displayed incorrectly, use the /simplelist.', parse_mode='HTML')


@bot.message_handler(commands=['simplelist'])
async def simple_list(message):
    with open('files/camera.json', 'r') as f:
        data = json.load(f)

    table = pt.PrettyTable(['ID', 'State', 'Name'])
    table.border = False
    table.align['ID'] = 'r'
    table.align['State'] = 'l'
    table.align['Name'] = 'l'

    for id, camera in data.items():
        table.add_row([id, "Enabled" if camera[1] else "Disabled", camera[0]])

    await bot.reply_to(message, f'<pre>{table}</pre>', parse_mode='HTML')


@bot.message_handler(commands=['disablecamera'])
async def disable_camera(message):
    with open('files/admins.json', "r") as f:
        data = json.load(f)

    if message.from_user.id not in data:
        await bot.reply_to(message, "Authorization failed.")
        return

    msg = await bot.reply_to(message, f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nDisabling camera...")

    try:
        cameraid = message.text.split()[1:][0]
    except:
        await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nDisabling camera... Error - Attribute required!", message.chat.id, msg.id)
        return

    with open('files/camera.json', 'r+') as f:
        data = json.load(f)

        if cameraid not in data:
            await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nDisabling camera... Error - Camera not found.", message.chat.id, msg.id)
            return

        data[cameraid][1] = False
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()

    await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nDisabling camera... Done!", message.chat.id, msg.id)


@bot.message_handler(commands=['enablecamera'])
async def disable_camera(message):
    with open('files/admins.json', "r") as f:
        data = json.load(f)

    if message.from_user.id not in data:
        await bot.reply_to(message, "Authorization failed.")
        return

    msg = await bot.reply_to(message, f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nEnabling camera...")

    try:
        cameraid = message.text.split()[1:][0]
    except:
        await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nDisabling camera... Error - Attribute required!", message.chat.id, msg.id)
        return

    with open('files/camera.json', 'r+') as f:
        data = json.load(f)

        if cameraid not in data:
            await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nEnabling camera... Error - Camera not found.", message.chat.id, msg.id)
            return
        
        data[cameraid][1] = True
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()

    await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nEnabling camera... Done!", message.chat.id, msg.id)


@bot.message_handler(commands=['init'])
async def add_chat(message) -> None:
    with open('files/admins.json', "r") as f:
        data = json.load(f)

    if message.from_user.id not in data:
        await bot.reply_to(message, "Authorization failed.")
        return

    msg = await bot.reply_to(message, f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering a chat...")

    with open('files/chats.json', 'r+') as f:
        data = json.load(f)

        if message.chat.id in data:
            await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nError: chat is already in the whitelist", message.chat.id, msg.id)
            return
        
        data.append(message.chat.id)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()
    
    await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering a chat... Done!", message.chat.id, msg.id)
    

@bot.message_handler(commands=['getuserid'])
async def get_id(message) -> None:
    await bot.reply_to(message, f"Your id is `{message.from_user.id}`", parse_mode='Markdown')


@bot.message_handler(commands=['addadmin'])
async def add_admin(message) -> None:
    with open('files/admins.json', "r+") as f:
        data = json.load(f)

    if message.from_user.id not in data:
        await bot.reply_to(message, "Authorization failed.")
        return

    msg = await bot.reply_to(message, f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering new admin...")

    try:
        admin_id = message.text.split()[1:][0]
    except:
        await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nCan not process empty request.", message.chat.id, msg.id)
        return

    try:
        admin_id = int(admin_id)
    except:
        await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nError while converting adminID to integer.", message.chat.id, msg.id)
        return

    if admin_id in data:
        await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nError: admin is already registered.", message.chat.id, msg.id)
        return
    
    with open('files/admins.json', "r+") as f:
        data = json.load(f)

        data.append(admin_id)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()
    
    await bot.edit_message_text(f"The request is authorized. Welcome to the system, @{message.from_user.username}\n\nRegistering admin... Done!", message.chat.id, msg.id)


async def run_bot():
    while True:
        try:
            await bot.polling()
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    print("hta-v0.3.1.2 Starting...")
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

    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(main(), run_bot())
    loop.run_until_complete(tasks)