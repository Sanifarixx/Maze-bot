import aiohttp
import disnake

async def getUserAvatar(member: disnake.Member):
    if member.avatar:
        avatar_url = member.avatar.url
    else:
        avatar_url = member.default_avatar

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as r:
            file = await r.read()
            return file
