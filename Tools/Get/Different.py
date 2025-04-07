from datetime import datetime
import disnake
import aiohttp
import asyncio
import time

from config import USER_AUTH_TOKEN


async def getOrganizationalRoles(self, guildId: int) -> list:
    config = self.bot.db.get_config(guildId)
    if config:
        if config['organizationalRoles']:
            roles = config['organizationalRoles']
        else:
            roles = []
    else:
        roles = []

    return roles

async def get_time_difference(message: disnake.Message):
    message_timestamp = datetime.fromtimestamp(message.created_at.timestamp())
    now = datetime.now()
    time_difference = now - message_timestamp
    seconds = time_difference.total_seconds()
    if seconds < 60:
        return f"`Запрос был рассмотрен за {int(seconds)} секунд`"
    elif seconds < 120:
        return f"`Запрос был рассмотрен за {int(seconds / 60)} минуту`"
    elif seconds<300:
        return f"`Запрос был рассмотрен за {int(seconds / 60)} минуты`"
    elif seconds < 3600:
        return f"`Запрос был рассмотрен за {int(seconds / 60)} минут`"
    else:
        return f"`Запрос был рассмотрен за {int(seconds / 3600)} часов`"


async def convert_to_seconds(duration):
    multiplier = {'s' : 1, 'm' : 60, 'h' : 3600, 'd' : 86400, 'w' : 604800}
    return int(duration[:-1]) * multiplier[duration[-1]] 

async def time_diff():
    return int(time.time())

async def count_user_messages(start_date: str, end_date: str, member_id: int, guild_id: int, channel_id: int, flag: bool = None) -> int:
    try:
        headers = {
            "Authorization": USER_AUTH_TOKEN,
        }

        url = f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?channel_id={channel_id}&author_id={member_id}&include_nsfw=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as r:
                data = await r.json()
        if flag:
            return data['total_messages']
    except:
        return 0

async def count_messages(self, start_date: str, end_date: str, member_id: int, guild_id: int, channel_id: int):
    start_date_object  = datetime.strptime(start_date, "%d.%m.%Y")
    end_date_object = datetime.strptime(end_date, "%d.%m.%Y")
    i = 0
    messages = await self.bot.db.get_messages(guild_id, member_id)
    async for message in messages:
        if message['channelId'] == channel_id:
            message_date_object = datetime.strptime(message['date'], "%d.%m.%Y")
            if start_date_object <= message_date_object <= end_date_object:
                i += 1
    return i

async def check_message(message, start_date_object, end_date_object):
    fromiso = datetime.fromisoformat(message[0]['timestamp'])
    message_timestamp_str = f"{fromiso.day}.{fromiso.month}.{fromiso.year}"
    message_timestamp_formatted = datetime.strptime(message_timestamp_str, "%d.%m.%Y")
    if start_date_object <= message_timestamp_formatted <= end_date_object:
        return True
    return False