import disnake
from disnake.ext import commands, tasks
import chat_exporter

from Classes.CustomClient import CustomClient
from Tools.Get.Different import time_diff
from Classes.CustomClient import CustomClient
from Tools.Get.Log import getModerationLogChannel

class Parsers(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot = bot
        self.check_punish_loop.start()

    def cog_unload(self):
        self.check_punish_loop.cancel()

    @tasks.loop(seconds=5)
    async def check_punish_loop(self):
        for guild in self.bot.guilds:
            config = await self.bot.db.get_config(guild.id)
            punishments = await self.bot.db.get_punish({'endTime': {'$ne': None, "$lt": await time_diff()}, 'guildId': guild.id}, many=True)
            async for punish in punishments:
                if punish['type'] in ['MUTE', 'VMUTE', 'MPMUTE', 'TICKETBAN', 'BANROLEREQUEST', 'BAN']:
                    if punish['type'] == 'BAN':
                        member = await self.bot.fetch_user(punish['memberId'])
                        await guild.unban(user=member, reason='Durata pedepsei a expirat')
                    else:
                        member = disnake.utils.get(guild.members, id=punish['memberId'])
                        if member:
                            if punish['type'] == 'MUTE':
                                role = disnake.utils.get(guild.roles, name='Muted')
                            if punish['type'] == 'VMUTE':
                                role = disnake.utils.get(guild.roles, name='Voice Muted')
                            if punish['type'] == 'MPMUTE':
                                role = disnake.utils.get(guild.roles, name='MarketPlace Muted')
                            if punish['type'] == 'BANROLEREQUEST':
                                role = disnake.utils.get(guild.roles, name='Role Banned')
                            if punish['type'] == 'TICKETBAN':
                                role = disnake.utils.get(guild.roles, name='Ticket Banned')

                            await member.remove_roles(role)

                            channel = await getModerationLogChannel(self, guild.id)
                            if channel:

                                embed = disnake.Embed(title=f"[UN{punish['type']}] {member.display_name}", colour=disnake.Colour.default(), timestamp=disnake.utils.utcnow())
                                embed.add_field(name='Moderator', value="Sistem",  inline=True)
                                embed.add_field(name='Utilizator', value=f'{member.mention}',  inline=True)
                                embed.add_field(name='Motiv', value="Durata pedepsei a expirat",  inline=True)
                                embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

                                await channel.send(embed=embed)

                        await self.bot.db.update_punish({'type': punish['type'], 'guildId': guild.id, 'memberId': member.id, 'endTime': {'$ne': None}}, {'endTime': None})

                if punish['type'] == 'TICKET':
                    channel = self.bot.get_channel(config['ticketLog'])
                    ticketChannel = self.bot.get_channel(punish['memberId'])
                    if ticketChannel:
                        if channel:
                            file = await chat_exporter.quick_export(ticketChannel)

                            embed = disnake.Embed(title='🗑 ❘ Ștergerea unui tichet')
                            embed.add_field(name='Moderator', value="Sistem",  inline=True)
                            embed.add_field(name='Tichet', value=f"`({ticketChannel.name})` `[{ticketChannel.id}]`",  inline=True)
                            embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)
                            await channel.send(embed=embed, file=file)

                        await self.bot.db.update_punish({'memberId': ticketChannel.id}, {'endTime': None})
                        await ticketChannel.delete()

                if punish['type'] == 'NOTIFY':
                    modersNotifyChannel = self.bot.get_channel(config['notifynotifychannel'])
                    if modersNotifyChannel:
                        embed = disnake.Embed(description=f"Durata [notificării](https://discord.com/channels/{guild.id}/{config['notifychannel']}/{punish['notifyMessageId']}) a expirat!", color=disnake.Colour.yellow())
                        embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)
                        await modersNotifyChannel.send(f"<@{punish['moderId']}>", embed=embed)
                    message = self.bot.get_message(punish['notifyMessageId'])
                    if message:
                        await message.edit(components=[])
                    await self.bot.db.update_punish({'notifyMessageId': punish['notifyMessageId']}, {'endTime': None})

def setup(bot: CustomClient):
    bot.add_cog(Parsers(bot))
