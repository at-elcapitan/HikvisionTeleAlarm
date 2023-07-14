**HikvisionTeleAlarm** is simple bot written on **Python** that uses `telebot` and `hikvisionapi` libs, to chatch motion alerts from camera system and send messages to setted telegram chats or groups.

## Installation
HikvisionTeleAlarm requires `Python 3.10` (using the bot on early versions does not guarantee correct functioning) and created telegram bot using [@BotFather](https://t.me/BotFather).

#### Linux
```bash
git clone https://github.com/at-elcapitan/HikvisionTeleAlarm.git
```
or
```bash
wget https://github.com/at-elcapitan/HikvisionTeleAlarm/archive/refs/tags/pda-v0.3.1.1.zip && unzip pda-v0.3.1.1.zip && rm pda-v0.3.1.1.zip
```
#### Windows
```bash
git clone https://github.com/at-elcapitan/HikvisionTeleAlarm.git`
```
or
```bash
curl -sL "https://github.com/at-elcapitan/HikvisionTeleAlarm/archive/refs/tags/pda-v0.3.1.1.zip" -o pda-v0.3.1.1.zip
```
## Getting started
Before starting the bot, create a `.env` file according to the template and fill it with your data:
```
TOKEN = SOMETOKEN
HOST = SOMEHOST
LOGIN = SOMELOGIN
PASSWD = SOMEPASSWD
TIMEOUT = 15
```
**Do not use ""**

### Starting bot
#### Linux
```
chmod +x ./run.sh && ./run.sh
```

#### Windows (PowerShell)
```
python -m pip install virtualenv && virtualenv venv && venv\Scripts\activate
```

After running the bot for the first time, run the `/getuserid` command and shut it down. The bot will create a `files` directory as well as .json configs.
Copy your user id and paste it to `admins.json` file. Example:
```js
[
    0011223344
]
```

Change `camera.json` file using template:
> ID - camera ID in HIKVISION system (must be an integer placed in "")
> 
> name - displaying name
> 
> `true | false` - isEnabled state.
```js
{
    "ID": [
        "name",
        false
    ],
    "ID2": [
        "name2",
        true
    ]
}
```

Simple annotation for all bot commands:
```
init - Adding chat to send list [Auth required]
simplelist - Displaying information about cameras [Simplified]
list - Displaying information about cameras [Prettytable]
disablecamera - <id> Disabling camera [Auth required/Attribute required]
enablecamera - <id> Enabling camera [Auth required/Attribute required]
getuserid - Displaying user id
addadmin - <id> Adding new admin to the list [Auth required/Attribute required]
```

## Bot commands
`/init` - requires admin privileges (user id must be in `admins.json` file), adds chat or group id to `chats.json`

`/list` - sending information about all cameras (IDs, isEnabled)

`/simplelist` - simple form of `/list` command (w/o borders)

`/disablecamera | /enablecamera` - changing isEnabled state of camera

`/getuserid` - sending user ID to chat

`/addadmin` - adds user id to the `admins.json` file
