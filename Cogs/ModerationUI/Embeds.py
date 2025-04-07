import disnake
from typing import Optional

from config import DM_DATA, RESPONSE_DATA, TYPES_WITH_DURATION
from Classes.Punish import Punish
from Tools.Get.Log import getModerationLogChannel

async def send_punish_response(self, inter: disnake.ApplicationCommandInteraction, punish: Punish) -> disnake.Message:

    embed=disnake.Embed(title=RESPONSE_DATA[punish.type][0], description=f"{punish.member.mention} {RESPONSE_DATA[punish.type][1]} {inter.author.mention}", colour=disnake.Colour.default()) 
    embed.add_field(name='Motivul', value=f'{punish.reason}',  inline=True)  # "Причина" -> "Motivul"
    if punish.type in TYPES_WITH_DURATION:
        embed.add_field(name='Termenul de finalizare', value=f'<t:{punish.endTime}>',  inline=True)  # "Срок окончания" -> "Termenul de finalizare"
    embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

    await inter.response.send_message(embed=embed)

async def send_punish_dm(self, punish: Punish) -> Optional[disnake.Message]:

    description = f'Moderator:`{punish.inter.author.display_name} [{punish.inter.author.id}]`'f'\nMotiv:`{punish.reason}`'  # "Модератор" -> "Moderator", "Причина" -> "Motiv"
    if punish.type in TYPES_WITH_DURATION:
        description += f'\nData expirării sancțiunii:<t:{punish.endTime}>'  # "Дата окончания наказания" -> "Data expirării sancțiunii"
    embed=disnake.Embed(title=f"{DM_DATA[punish.type]} {punish.member.guild.name}", description=description,colour=disnake.Colour.red())
    embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

    try:
        await punish.member.send(embed=embed)
    except:
        pass

async def send_punish_log(self, punish: Punish) -> Optional[disnake.Message]:
    channel = await getModerationLogChannel(self, punish.member.guild.id)
    if channel:
        embed=disnake.Embed(title=f'[{punish.type}] {punish.member.display_name}', colour=disnake.Colour.default(), timestamp=disnake.utils.utcnow()) 
        embed.add_field(name='Moderator', value=punish.inter.author.mention,  inline=True)  # "Модератор" -> "Moderator"
        embed.add_field(name='Utilizator', value=punish.member.mention,  inline=True)  # "Пользователь" -> "Utilizator"
        embed.add_field(name='Motiv', value=punish.reason, inline=True)  # "Причина" -> "Motiv"
        if punish.type in TYPES_WITH_DURATION:
            embed.add_field(name='Durata sancțiunii', value=punish.duration,  inline=True)  # "Срок наказания" -> "Durata sancțiunii"
            embed.add_field(name='Data expirării sancțiunii', value=f'<t:{punish.endTime}>',  inline=True)  # "Дата окончания наказания" -> "Data expirării sancțiunii" 
        embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

        try:
            await channel.send(embed=embed)
        except:
            pass
