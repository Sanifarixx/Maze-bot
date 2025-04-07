import disnake
from disnake.ext import commands
from datetime import datetime
from disnake import TextChannel
import asyncio

from config import DELETE_ERROR_SECONDS
from Classes.CustomClient import CustomClient
from Classes.Punish import Punish
from Tools.Get.Access import getModerAccess, getBanAccess
from Tools.Get.Check import is_valid_date, is_date_in_range, check_punish_duration_format
from Tools.GeneralUI import ErrEmbed
from Tools.Get.Log import getModerationLogChannel
from Tools.Get.Different import count_messages, time_diff, convert_to_seconds, getOrganizationalRoles
from Cogs.ModerationUI.TicketUI import ticketCreateButton, ticketButtons
from Cogs.ModerationUI.NotifyUI import notifyCancelButton, notifyDropDownView
from Cogs.ModerationUI.RoleRequestUI import RoleRequestButtons, RoleRequestDropDown, RoleRequestModal
from Cogs.ModerationUI.BanRequestUI import banRequestButtons, banRequestModal
from Cogs.ModerationUI.getModerStatUI import getModerStatButtonsEphemeralFalse, getModerStatButtonsEphemeralTrue
from Cogs.ModerationUI.Embeds import send_punish_dm, send_punish_log, send_punish_response

class Moderation(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot = bot
        self.bot.add_view(banRequestButtons(bot = self.bot))
        self.bot.add_view(ticketButtons(bot = self.bot))
        self.bot.add_view(ticketCreateButton(bot = self.bot))
        self.bot.add_view(RoleRequestButtons(bot = self.bot))
        self.bot.add_view(notifyCancelButton(bot = self.bot))

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.slash_command(description='Dă afara un utilizator')
    async def kick(self, inter: disnake.ApplicationCommandInteraction, 
                   member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)', name='utilizator'), 
                   reason: str=commands.Param(description='Motiv', name='motiv')):

        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces lipsă pentru moderare'])
        
        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți aplica o sancțiune unui moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        if member.top_role.position >= inter.guild.me.top_role.position:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu ai suficiente permisiuni pentru a da afara acest utilizator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        punish = Punish(inter=inter, type='KICK', member=member, reason=reason)
        try:
            await send_punish_response(self, inter, punish)
            await send_punish_dm(self, punish)

            await inter.guild.kick(member, reason=reason)

            await send_punish_log(self, inter.guild.id, punish)
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Banează un utilizator')
    async def ban(self, inter: disnake.ApplicationCommandInteraction, 
                  member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)', name='utilizator'), 
                  duration: str=commands.Param(description='Durata banului (s/m/h/d/w)', name='durată'), 
                  reason: str=commands.Param(description='Motiv', name='motiv')):
        
        if not await getBanAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces lipsă pentru banare'])
        
        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți aplica o sancțiune unui moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        if member.top_role.position >= inter.guild.me.top_role.position:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu ai suficiente permisiuni pentru a bana acest utilizator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
                
        if not await check_punish_duration_format(duration):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Format incorect pentru durata sancțiunii!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            
        punish = Punish(inter=inter, type='BAN', member=member, reason=reason, duration=duration, endTime = await time_diff() + await convert_to_seconds(duration))

        try:
            await send_punish_response(self, inter, punish)
            await send_punish_dm(self, punish)

            await inter.guild.ban(member, reason=reason)

            await send_punish_log(self, inter.guild.id, punish)
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Debanează un utilizator')
    async def unban(self, inter:disnake.ApplicationCommandInteraction, 
                    member: disnake.User=commands.Param(description='Utilizator (menționare sau id)',name='utilizator'), 
                    reason: str=commands.Param(description='Motiv',name='motiv')):
        if not await getBanAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces lipsă pentru banare'])

        try:
            await inter.guild.fetch_ban(member)

            punish = Punish(inter, type='UNBAN', member=member, reason=reason)

            await send_punish_response(self, inter, punish)

            await inter.guild.unban(member, reason=reason)

            await send_punish_log(self, punish)
            await self.bot.db.update_punish({'guildId': inter.guild.id, 'userId': member.id, 'type': 'BAN'}, {'endTime': None})
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            if Exception == disnake.NotFound:
                await inter.response.send_message(embed=await ErrEmbed(self, 'Utilizatorul nu este banat!'), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            else:
                await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Pune pe mut un utilizator')
    async def mute(self, inter: disnake.ApplicationCommandInteraction, 
                   member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)',name='utilizator'), 
                   duration: str=commands.Param(description='Durata mutului (m/h/d/w)',name='durată'), 
                   reason: str=commands.Param(description='Motiv',name='motiv')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces lipsă pentru moderare'])

        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți aplica o sancțiune unui moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        if not await check_punish_duration_format(duration):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Format incorect pentru durata sancțiunii!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        role = disnake.utils.get(inter.guild.roles, name='Muted')
        if role in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul este deja pe mut!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS) 

        punish = Punish(inter=inter, type='MUTE', member=member, reason=reason, duration=duration, endTime = await time_diff() + await convert_to_seconds(duration))

        try:
            await send_punish_response(self, inter, punish)
            await send_punish_dm(self, punish)

            await member.add_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Scoate mutul unui utilizator')
    async def unmute(self, inter:disnake.ApplicationCommandInteraction, 
                     member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)',name='utilizator'), 
                     reason: str=commands.Param(description='Motiv',name='motiv')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces lipsă pentru moderare'])
        
        role=disnake.utils.get(inter.guild.roles, name='Muted')
        if role not in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul nu este pe mut!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            
        punish = Punish(inter=inter, type='UNMUTE', member=member, reason=reason)

        try:
            await send_punish_response(self, inter, punish)

            await member.remove_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.update_punish({'guildId': inter.guild.id, 'userId': member.id, 'type': 'MUTE'}, {'endTime': None})
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Blochează accesul unui utilizator la piața de tranzacții')
    async def mpmute(self, inter: disnake.ApplicationCommandInteraction, 
                     member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)',name='utilizator'), 
                     duration: str=commands.Param(description='Durata mutului (m/h/d/w)',name='durată'),
                     reason: str=commands.Param(description='Motiv',name='motiv')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces lipsă pentru moderare'])
        
        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți aplica o sancțiune unui moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        if not await check_punish_duration_format(duration):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Format incorect pentru durata sancțiunii!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        role=disnake.utils.get(inter.guild.roles, name='MarketPlace Muted')
        if role in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul este deja în mut!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        punish = Punish(inter=inter, type='MPMUTE', member=member, reason=reason, duration=duration, endTime = await time_diff() + await convert_to_seconds(duration))
        try:
            await send_punish_response(self, inter, punish)
            await send_punish_dm(self, punish)

            await member.add_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Deblochează accesul la piața utilizatorului')
    async def unmpmute(self, inter:disnake.ApplicationCommandInteraction, 
                       member: disnake.Member=commands.Param(description='Utilizator (Menționare sau id)',name='utilizator'), 
                       reason: str=commands.Param(description='Motivul',name='motvul')):

        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces moderare'])
        
        role=disnake.utils.get(inter.guild.roles, name='MarketPlace Muted')
        if role not in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul nu este în mut!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        punish = Punish(inter=inter, type='UNMPMUTE', member=member, reason=reason)
        try:
            await send_punish_response(self, inter, punish)

            await member.remove_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.update_punish({'guildId': inter.guild.id, 'userId': member.id, 'type': 'MPMUTE'}, {'endTime': None})
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Muta utilizatorul în voce')
    async def vmute(self, inter: disnake.ApplicationCommandInteraction, 
                    member: disnake.Member=commands.Param(description='Utilizator (Menționare sau id)',name='utilizator'), 
                    duration: str=commands.Param(description='Durata mutului (m/h/d/w)',name='durată'),
                     reason: str=commands.Param(description='Motivul',name='motvul')):

        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces moderare'])
        
        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți muta un moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        role=disnake.utils.get(inter.guild.roles, name='Voice Muted')
        if role in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul este deja în mut!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        if not await check_punish_duration_format(duration):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Formatul duratei pedepsei este greșit!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
        punish = Punish(inter=inter, type='VMUTE', member=member, reason=reason, duration=duration, endTime = await time_diff() + await convert_to_seconds(duration))
        try:
            await send_punish_response(self, inter, punish)
            await send_punish_dm(self, punish)

            await member.add_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Dezmută utilizatorul în voce')
    async def unvmute(self, inter:disnake.ApplicationCommandInteraction, 
                      member: disnake.Member=commands.Param(description='Utilizator (Menționare sau id)',name='utilizator'), 
                      reason: str=commands.Param(description='Motivul',name='motvul')):

        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces moderare'])
        
        role=disnake.utils.get(inter.guild.roles, name='Voice Muted')
        if role not in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul nu este în mut!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        punish = Punish(inter=inter, type='UNVMUTE', member=member, reason=reason)
        try:
            await send_punish_response(self, inter, punish)

            await member.remove_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.update_punish({'guildId': inter.guild.id, 'userId': member.id, 'type': 'VMUTE'}, {'endTime': None})
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Șterge mesajele din canal' )
    @commands.cooldown(1, 10.0, commands.BucketType.user)
    async def clear(self, inter:disnake.ApplicationCommandInteraction, 
                    amount: int=commands.Param(description='Numărul de mesaje pentru ștergere (nu mai mult de 20)',name='cantitate')):

        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces moderare'])
        
        if amount > 20:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Numărul de mesaje pentru ștergere nu poate depăși 50!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        await inter.response.defer(ephemeral=True)
        await inter.channel.purge(limit=amount)
        await inter.edit_original_response(f'S-au șters {amount} mesaje!')
        channel = await getModerationLogChannel(self, inter.guild.id)
        if channel:
            embed=disnake.Embed(title='Ștergere mesaje', description=f"Șters de: {inter.author.mention}\nCanal: {inter.channel.mention}\nNumăr: {amount}", timestamp=disnake.utils.utcnow(), color = disnake.Colour.blue())
            embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)
            await channel.send(embed=embed)

    @commands.slash_command(description='Vezi lista de infracțiuni ale utilizatorului')
    async def infractions(self, inter:disnake.ApplicationCommandInteraction, 
                          user: disnake.User=commands.Param(description='Utilizator (Menționare sau id)',name='utilizator'),
                          everywhere: bool = commands.Param(description='Căutare pe toate serverele', name='global', default=None, choices=[True, False])):

        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces moderare'])
         
        await inter.response.defer()

        if everywhere:
            punishments = await self.bot.db.get_punish({'memberId': user.id}, True)
        else:
            punishments = await self.bot.db.get_punish({'memberId': user.id, 'guildId': inter.guild.id}, True)

        embed=disnake.Embed(colour=disnake.Colour.blue())
        embed.description = ''
        async for item in punishments:

            if item['duration']!=None and item['reason'] !=None:
                punishStr = f"**`[{item['type']}]` | <t:{item['timeNow']}> | {item['duration']} | {item['reason']} ||**<@{item['moderId']}>"

            if item['duration']==None and item['reason']!=None:
                punishStr = f"**`[{item['type']}]` | <t:{item['timeNow']}> | {item['reason']} ||**<@{item['moderId']}>"

            if item['reason']==None and item['duration']==None:
                    punishStr = f"**`[{item['type']}]` | <t:{item['timeNow']}> ||**<@{item['moderId']}>"

            if item['duration']!=None and item['reason']==None:
                punishStr = f"**`[{item['type']}]` | <t:{item['timeNow']}> | {item['duration']} ||**<@{item['moderId']}>"

            embed.description = embed.description + punishStr + '\n'

        embed.set_author(name=f'{user.display_name} ➤Lista infracțiunilor', icon_url=user.avatar.url if user.avatar else user.default_avatar.url)

        await inter.edit_original_response(embed=embed)
        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

    @commands.slash_command(description='Blochează accesul utilizatorului la tichete')
    async def ticketban(self, inter:disnake.AppCommandInteraction, 
                        member:disnake.Member=commands.Param(description='Utilizator (Menționare sau id)',name='utilizator'), 
                        duration:str=commands.Param(description='Durata blocării (m/h/d/w)',name='durată'), 
                        reason:str=commands.Param(description='Motivul',name='motvul')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces moderare'])

        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu se poate aplica mute unui moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        role = disnake.utils.get(inter.guild.roles, name='Ticket Banned')
        if role in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul este deja sub mute!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        if not await check_punish_duration_format(duration):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Formatul duratei pedepsei este incorect!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        punish = Punish(inter=inter, type='TICKETBAN', member=member, reason=reason, duration=duration, endTime = await time_diff() + await convert_to_seconds(duration))
        try:
            await send_punish_response(self, inter, punish)
            await send_punish_dm(self, punish)

            await member.add_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Deblochează accesul la tichete')
    async def unticketban(self, inter:disnake.ApplicationCommandInteraction, 
                          member: disnake.Member=commands.Param(description='Utilizator (Mențiune sau id)', name='utilizator'), 
                          reason: str=commands.Param(description='Motivul', name='motiv')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces de moderare'])
        
        role = disnake.utils.get(inter.guild.roles, name='Ticket Banned')
        if role not in member.roles:
            return await inter.response.send_message(embed=await ErrEmbed(self, "Utilizatorul nu are blocarea tichetelor!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        punish = Punish(inter=inter, type='UNTICKETBAN', member=member, reason=reason)
        try:
            await send_punish_response(self, inter, punish)

            await member.remove_roles(role)

            await send_punish_log(self, punish)
            await self.bot.db.update_punish({'guildId': inter.guild.id, 'userId': member.id, 'type': 'TICKETBAN'}, {'endTime': None})
            await self.bot.db.insert_punish(await punish.to_dict())
        except Exception as e:
            await inter.followup.send(e, ephemeral=True)

    @commands.slash_command(description='Obține statistica moderatorului')
    async def getmoderstat(self, inter:disnake.ApplicationCommandInteraction,
                           fromdate:str=commands.Param(description='Data de început (dd.mm.yyyy)'),
                           mod: disnake.Member=commands.Param(description='Moderator (Mențiune sau id)', default=None),
                           todate: str=commands.Param(default=datetime.now().strftime("%d.%m.%Y"), description='Data de sfârșit (dd.mm.yyyy)'), 
                           ephemeral:bool=commands.Param(default=True, description='Ascunde mesajul?')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Lipsă acces de moderare'])

        if not await is_valid_date(fromdate) or not await is_valid_date(todate):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Formatul datei este incorect!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

        await inter.response.defer(ephemeral=ephemeral)
        embed = disnake.Embed(title=f'Statistici moderatori din {fromdate} până în {todate}', colour=disnake.Colour.blue())
        config = await self.bot.db.get_config(inter.guild.id)

        mods = []
        if mod:
            mods.append([mod.id, mod.display_name])
        else:
            role = disnake.utils.get(inter.guild.roles, id=config['normarole'])
            if role:
                for member in role.members:
                    mods.append([member.id, member.display_name])
        
        countMods = len(mods)

        endPage = (countMods // 6) + 1 if countMods % 2 != 0 else countMods // 6

        embed.set_footer(text=f'Pagina 1 / {endPage}', icon_url=self.bot.user.display_avatar.url)

        i = 0
        data = []
        view = None

        for moder in mods:
            punishments = await self.bot.db.get_punish({'moderId': moder[0], 'guildId': inter.guild.id}, many=True)

            count = 0
            countban = 0
            countkick = 0
            countvmute = 0
            countmute = 0
            countticket = 0
            countformaccept = 0
            countformreject = 0
            countticketban = 0
            async for item in punishments:
                type = item['type']
                date = item['date']
                if await is_date_in_range(date, fromdate, todate):
                    if type == "DELETE_BALL":
                        count += item['duration']
                    if type == 'BAN':
                        countban += 1
                        count += config['ballban']
                    if type == 'MUTE': 
                        countmute += 1
                        count += config['ballmute']
                    if type == 'TICKET':
                        countticket += 1
                        count += config['ballticket']
                    if type == 'VMUTE':
                        countvmute += 1
                        count += config['ballvmute']
                    if type == 'KICK':
                        countkick += 1
                        count += config['ballkick']
                    if type == 'FORM_ACCEPT':
                        countformaccept += 1 
                        count += config['ballformaccept']
                    if type == 'FORM_REJECT':
                        countformreject += 1
                        count += config['ballformreject']
                    if type == 'TICKETBAN':
                        countticketban += 1
                        count += config['ballticketban']

            if config['normachannel']:
                countmessages = await count_messages(self, fromdate, todate, moder[0], inter.guild.id, config['normachannel'])
            else:
                countmessages = 0

            result_balls = count + countmessages * config['ballmessage']
            i += 1
            if countMods > 6:
                data.append([i, inter.author.id, moder, f'Mute: {countmute}\nBan: {countban}\nKick: {countkick}\nVmute: {countvmute}\nTicketban: {countticketban}\nForm accept: {countformaccept}\nForm reject: {countformreject}\nClosed tickets: {countticket}\nMessages: {countmessages}\n \nTotal points: {result_balls:.2f}'])
            if i > 6:
                if ephemeral:
                    view = getModerStatButtonsEphemeralTrue(self.bot, data, inter.author, countMods, endPage)
                else:
                    view = getModerStatButtonsEphemeralFalse(self.bot, data, inter.author, countMods, endPage)
            else:
                embed.add_field(name=moder[1], value=f'Mute: {countmute}\nBan: {countban}\nKick: {countkick}\nVmute: {countvmute}\nForm accept: {countformaccept}\nForm reject: {countformreject}\nClosed tickets: {countticket}\nMessages: {countmessages}\n \nTotal points: {result_balls:.2f}', inline=True)
        await inter.edit_original_response(embed=embed, view=view)

    @commands.slash_command(description='Configurează punctele pentru pedepse')
    @commands.has_permissions(administrator=True)
    async def config_moderstat(self, inter:disnake.ApplicationCommandInteraction,
                mute:float=commands.Param(description='puncte pentru mute', name='mute', default=None),
                ban:float=commands.Param(description='puncte pentru ban', name='ban', default=None),
                kick:float=commands.Param(description='puncte pentru kick', name='kick', default=None),
                ticket:float=commands.Param(description='puncte pentru închiderea tichetului', name='ticket', default=None),
                rolerequest:float=commands.Param(description='puncte pentru acordarea unui rol', name='role-request', default=None),
                roleremove:float=commands.Param(description='puncte pentru îndepărtarea unui rol', name='role-remove', default=None),
                ticketban:float=commands.Param(description='puncte pentru acordarea unui ticketban', name='ticketban', default=None),
                formaccept:float=commands.Param(description='puncte pentru acceptarea unui formular pentru ban', name='form-accept', default=None),
                formreject:float=commands.Param(description='puncte pentru refuzul formularului pentru ban', name='form-reject', default=None),
                mpmute:float=commands.Param(description='puncte pentru mute pe MP', name='mpmute', default=None),
                vmute:float=commands.Param(description='puncte pentru mute pe voice', name='vmute', default=None),
                message:float=commands.Param(description='puncte pentru mesaj', name='message', default=None),
                normarole:disnake.Role=commands.Param(description='rolul pentru care se calculează punctele', name='role', default=None),
                normachannel:TextChannel=commands.Param(description='canalul în care se calculează mesajele', name='channel', default=None)):
        config = await self.bot.db.get_config(inter.guild.id)
        if not config:
            return await inter.response.send_message("Configurația serverului nu a fost găsită, folosește comanda /config", ephemeral=True)

        embed = disnake.Embed(title="Modificări:", timestamp=disnake.utils.utcnow())
        if mute:
            await self.bot.db.update_config(inter.guild.id, {'ballmute': mute})
            embed.add_field(name='Puncte pentru mute:', value=mute, inline=False)
        if mute:
            await self.bot.db.update_config(inter.guild.id, {'ballmute': mute})
            embed.add_field(name='Puncte pentru mute:', value=mute, inline=False)
        if ban:
            await self.bot.db.update_config(inter.guild.id, {'ballban': ban})
            embed.add_field(name='Puncte pentru ban:', value=ban, inline=False)
        if kick:
            await self.bot.db.update_config(inter.guild.id, {'ballkick': kick})
            embed.add_field(name='Puncte pentru kick:', value=kick, inline=False)
        if ticket:
            await self.bot.db.update_config(inter.guild.id, {'ballticket': ticket})
            embed.add_field(name='Puncte pentru închiderea tichetului:', value=ticket, inline=False)
        if rolerequest:
            await self.bot.db.update_config(inter.guild.id, {'ballrolerequest': rolerequest})
            embed.add_field(name='Puncte pentru acordarea rolului:', value=rolerequest, inline=False)
        if roleremove:
            await self.bot.db.update_config(inter.guild.id, {'ballroleremove': roleremove})
            embed.add_field(name='Puncte pentru îndepărtarea rolului:', value=roleremove, inline=False)
        if ticketban:
            await self.bot.db.update_config(inter.guild.id, {'ballticketban': ticketban})
            embed.add_field(name='Puncte pentru ticketban:', value=ticketban, inline=False)
        if formaccept:
            await self.bot.db.update_config(inter.guild.id, {'ballformaccept': formaccept})
            embed.add_field(name='Puncte pentru acceptarea formularului:', value=formaccept, inline=False)
        if formreject:
            await self.bot.db.update_config(inter.guild.id, {'ballformreject': formreject})
            embed.add_field(name='Puncte pentru refuzul formularului:', value=formreject, inline=False)
        if mpmute:
            await self.bot.db.update_config(inter.guild.id, {'ballmpmute': mpmute})
            embed.add_field(name='Puncte pentru mp mute:', value=mpmute, inline=False)
        if vmute:
            await self.bot.db.update_config(inter.guild.id, {'ballvmute': vmute})
            embed.add_field(name='Puncte pentru voice mute:', value=vmute, inline=False)
        if message:
            await self.bot.db.update_config(inter.guild.id, {'ballmessage': message})
            embed.add_field(name='Puncte pentru mesaj:', value=message, inline=False)
        if normarole:
            await self.bot.db.update_config(inter.guild.id, {'normarole': normarole.id})
            embed.add_field(name='Rol pentru statistici:', value=normarole.mention, inline=False)
        if normachannel:
            await self.bot.db.update_config(inter.guild.id, {'normachannel': normachannel.id})
            embed.add_field(name='Canal pentru statistici:', value=normachannel.mention, inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)

        channel = await getModerationLogChannel(self, inter.guild.id)
        if channel:
            await channel.send(f"`Modificat de: {inter.author.id}`\n**Modificări în /config_moderstat**", embed=embed)


    @commands.slash_command(description='Configurează setările de moderare')
    @commands.has_permissions(administrator=True)
    async def config_moderation(self, inter:disnake.ApplicationCommandInteraction,
                                punishlog:TextChannel=commands.Param(description='Canal pentru logarea pedepselor', name='loguri_moderare', default=None),
                                ticketlog:TextChannel=commands.Param(description='Canal pentru logarea tichetelor', name='loguri_tichet', default=None),
                                ticketclose:str=commands.Param(description='ID categoria pentru tichetele închise', name='tichete-inchise', default=None),
                                ticketactive:str=commands.Param(description='ID categoria pentru tichetele active', name='tichete-active', default=None),
                                ticketzakrep:str=commands.Param(description='ID categoria pentru tichetele în curs de revizuire', name='tichete-in-revizuire', default=None),
                                formarole:disnake.Role=commands.Param(description='Rol pentru notificarea la crearea formularului de ban', name='rol-formular', default=None),
                                formachannel:TextChannel=commands.Param(description='Canal pentru trimiterea formularelor de ban', name='formulare-ban', default=None),
                                notifychannel:TextChannel=commands.Param(description='Canal pentru notificarea utilizatorilor', name='notificari', default=None),
                                notifynotifychannel:str=commands.Param(description='ID canal pentru notificarea moderatorilor despre expirarea notificării', name='notificari-expirate', default=None),
                                botnotify:TextChannel=commands.Param(description='Canal pentru notificările botului', name='bot-notificari', default=None),
                                getrolechannel:TextChannel=commands.Param(description='Canal pentru distribuirea rolurilor', name='distribuire-rol', default=None),
                                ticketrole:disnake.Role=commands.Param(description='Rol pentru notificarea la crearea unui tichet', name='rol-tichet', default=None),
                                orgroles:str=commands.Param(description='Formatul de introducere: Nume ID rol etichetă | Nume ID rol etichetă', name='roluri-organizationale', default=None),
                                add_moder_role:disnake.Role=commands.Param(description='Adăuga rol de moderator', name='adauga-rol-moderator', default=None),
                                dell_moder_role:disnake.Role=commands.Param(description='Elimina rol de moderator', name='elimina-rol-moderator', default=None),
                                add_banperm_role:disnake.Role=commands.Param(description='Adăuga rol cu permisiuni de ban', name='adauga-rol-perm-bana', default=None),
                                dell_banperm_role:disnake.Role=commands.Param(description='Elimina rol cu permisiuni de ban', name='elimina-rol-perm-bana', default=None)):
        config = await self.bot.db.get_config(inter.guild.id)
        if not config:
            return await inter.response.send_message("Configurarea serverului nu a fost găsită, folosește comanda /config", ephemeral=True)
        
        embed = disnake.Embed(title="Modificări:", timestamp=disnake.utils.utcnow())
        if punishlog:
            await self.bot.db.update_config(inter.guild.id, {'moderationLog': punishlog.id})
            embed.add_field(name='Canal pentru logarea pedepselor:', value=punishlog.mention, inline=False)
        if ticketlog:
            await self.bot.db.update_config(inter.guild.id, {'ticketLog': ticketlog.id})
            embed.add_field(name='Canal pentru logarea tichetelor:', value=ticketlog.mention, inline=False)
        if formarole:
            await self.bot.db.update_config(inter.guild.id, {'banRequestRole': formarole.id})
            embed.add_field(name='Rolul care va fi menționat la trimiterea formularului de ban:', value=formarole.mention, inline=False)
        if formachannel:
            await self.bot.db.update_config(inter.guild.id, {'banRequestChannel': formachannel.id})
            embed.add_field(name='Canalul pentru primirea formularului de ban:', value=formachannel.mention, inline=False)
        if notifychannel:
            await self.bot.db.update_config(inter.guild.id, {'notifychannel': notifychannel.id})
            embed.add_field(name='Canal pentru notificările utilizatorilor:', value=notifychannel.mention, inline=False)
        if notifynotifychannel:
            try:
                notifynotifychannnel = int(notifynotifychannel)
                await self.bot.db.update_config(inter.guild.id, {'notifynotifychannel': notifynotifychannnel})
                embed.add_field(name='Canal pentru notificările moderatorilor:', value=f'<#{notifynotifychannel}>', inline=False)
            except:
                embed.add_field(name='Nu s-a reușit adăugarea canalului pentru notificările moderatorilor:', value="Probabil, s-a introdus un număr incorect", inline=False)
        if botnotify:
            await self.bot.db.update_config(inter.guild.id, {'botnotify': botnotify.id})
            embed.add_field(name='Canal pentru notificările botului:', value=botnotify.mention, inline=False)
        if ticketactive:
            try:
                categoryId = int(ticketactive)
                await self.bot.db.update_config(inter.guild.id, {'ticketactive': categoryId})
                embed.add_field(name='ID categoria pentru tichetele active:', value=ticketactive, inline=False)
            except:
                embed.add_field(name='Nu s-a reușit adăugarea ID-ului pentru tichetele active:', value="Probabil, s-a introdus un număr incorect", inline=False)
        if ticketclose:
            try:
                categoryId = int(ticketclose)
                await self.bot.db.update_config(inter.guild.id, {'ticketclose': categoryId})
                embed.add_field(name='ID categoria pentru tichetele închise:', value=ticketactive, inline=False)
            except:
                embed.add_field(name='Nu s-a reușit adăugarea ID-ului pentru tichetele închise:', value="Probabil, s-a introdus un număr incorect", inline=False)
        if getrolechannel:
            await self.bot.db.update_config(inter.guild.id, {'getrolechannel': getrolechannel.id})
            embed.add_field(name='Canal pentru obținerea rolului:', value=getrolechannel.mention, inline=False)
        if ticketzakrep:
            try:
                categoryId = int(ticketzakrep)
                await self.bot.db.update_config(inter.guild.id, {'ticketzakrep': categoryId})
                embed.add_field(name='ID categoria pentru tichetele închise:', value=ticketactive, inline=False)
            except:
                embed.add_field(name='Nu s-a reușit adăugarea ID-ului pentru tichetele închise:', value="Probabil, s-a introdus un număr incorect", inline=False)
        if ticketrole:
            await self.bot.db.update_config(inter.guild.id, {'ticketrole': ticketrole.id})
            embed.add_field(name='Rolul care va fi menționat la crearea tichetului:', value=ticketrole.mention, inline=False)
        if add_moder_role:
            moderRoles = config['moderPermRoles']
            if add_moder_role.id not in moderRoles:
                moderRoles.append(add_moder_role.id)
                await self.bot.db.update_config(inter.guild.id, {'moderPermRoles': moderRoles})
                embed.add_field(name='Rol adăugat pentru moderare:', value=add_moder_role.mention, inline=False)
            else:
                embed.add_field(name='Nu s-a reușit adăugarea rolului de moderator', value='Rolul a fost deja adăugat', inline=False)
        if dell_moder_role:
            moderRoles: list = config['moderPermRoles']
            try:
                moderRoles.remove(dell_moder_role.id)
                await self.bot.db.update_config(inter.guild.id, {'moderPermRoles': moderRoles})
                embed.add_field(name='Rol eliminat de moderator:', value=dell_moder_role.mention, inline=False)
            except:
                embed.add_field(name='Nu s-a reușit eliminarea rolului de moderator', value='Rolul nu a fost găsit în baza de date', inline=False)

        if add_banperm_role:
            banRoles: list = config['banPermRoles']
            if add_banperm_role.id not in banRoles:
                banRoles.append(add_banperm_role.id)
                await self.bot.db.update_config(inter.guild.id, {'banPermRoles': banRoles})
                embed.add_field(name='Rol adăugat cu permisiuni pentru ban:', value=add_banperm_role.mention, inline=False)
            else:
                embed.add_field(name='Nu s-a reușit adăugarea rolului cu permisiuni de ban', value='Rolul a fost deja adăugat', inline=False)

        if dell_banperm_role:
            banRoles = config['banPermRoles']
            try:
                banRoles.remove(dell_banperm_role.id)
                await self.bot.db.update_config(inter.guild.id, {'banPermRoles': banRoles})
                embed.add_field(name='Rol eliminat cu permisiuni pentru ban:', value=dell_banperm_role.mention, inline=False)
            except:
                embed.add_field(name='Nu s-a reușit eliminarea rolului cu permisiuni de ban', value='Rolul nu a fost găsit în baza de date', inline=False)
        if orgroles:
            orgroles = orgroles.split('|')
            organizationalRoles = []
            organizationalRolesIds = []
            for item in orgroles:
                item = item.split()
                length = len(item)

                if length == 3:
                    organizationalRoles.append([item[0], int(item[1]), item[2]])
                    organizationalRolesIds.append(int(item[1]))
                if length == 4:
                    organizationalRoles.append([item[0] + ' ' + item[1],int(item[2]), item[3]])
                    organizationalRolesIds.append(int(item[2]))
                if length == 5:
                    organizationalRoles.append([item[0] + ' ' + item[1] + ' ' + item[2],int(item[3]), item[4]])
                    organizationalRolesIds.append(int(item[3]))
                if length == 6:
                    organizationalRoles.append([item[0] + ' ' + item[1] + ' ' + item[2] + ' ' + item[3], int(item[4]), item[5]])
                    organizationalRolesIds.append(int(item[4]))
                if length == 7:
                    organizationalRoles.append([item[0] + ' ' + item[1] + ' ' + item[2] + ' ' + item[3] + ' ' + item[4], int(item[5]), item[6]])
                    organizationalRolesIds.append(int(item[5]))

            await self.bot.db.update_config(inter.guild.id, {'organizationalRoles': organizationalRoles, 'organizationalRolesIds': organizationalRolesIds})
            embed.add_field(name='Roluri organizaționale:', value=organizationalRoles, inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)

        channel = await getModerationLogChannel(self, inter.guild.id)

        if channel:
            await channel.send(f"`Modificat de: {inter.author.id}`\n**Modificări în /config_moderstat**", embed=embed)

    @commands.slash_command(description="Trimite formular pentru ban")
    async def banrequest(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Missing moderation access'])
        
        if await getModerAccess(self, member):
            return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți trimite formularul pentru un moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS) 
        
        if inter.guild.me.top_role.position <= member.top_role.position:
                return await inter.response.send_message(embed=await ErrEmbed(self, "Nu am suficiente permisiuni pentru a trimite formularul!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS) 
        
        await inter.response.send_modal(modal=banRequestModal(bot=self.bot, member = member))

    @commands.slash_command(description='Notifică utilizatorul')
    async def notify (self, inter: disnake.ApplicationCommandInteraction, 
                      member: disnake.Member=commands.Param(description='Utilizator (mențiune sau id)',name='utilizator'), 
                      duration: str=commands.Param(description='Durata notificării (s/m/h/d/w)',name='durata'),
                      reason: str=commands.Param(description='Motivul',name='motiv')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Missing moderation access'])
        
        view = notifyDropDownView(bot=self.bot, reason=reason, duration=duration, author=inter.author, member=member)
        await inter.response.send_message(ephemeral=True, delete_after=30, view = view)     

    @commands.slash_command(description="Obține informații despre rol")
    @commands.has_permissions(administrator=True)
    async def rolemembers(self, inter:disnake.ApplicationCommandInteraction, role: disnake.Role=commands.Param(description='Rol (mențiune sau id)')):
                embed=disnake.Embed(description=f"**Utilizatori cu rolul: {role.mention}**", colour=disnake.Colour.blue())
                tasks = [embed.add_field(name="", value=f'{member.mention}', inline=False) for member in role.members]
                for member in role.members:
                        embed.add_field(name="", value=f'{member.mention}', inline=False)
                embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

                await inter.response.send_message(embed=embed)


    @commands.slash_command(description='Înlătură rolurile organizaționale sau aplică o blocare pentru cererea de rol')
    async def rr(self, inter: disnake.ApplicationCommandInteraction, 
                member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)'), 
                duration: str=commands.Param(default=None, description='Durata blocării cererii de rol (m/h/d/w)'), 
                reason: str=commands.Param(default=None, description='Motivul')):
        if not await getModerAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces de moderare lipsă'])
    
        if duration:
            if await getModerAccess(self, member):
                return await inter.response.send_message(embed=await ErrEmbed(self, "Nu poți pedepsi un moderator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
            if not await check_punish_duration_format(duration):
                return await inter.response.send_message(embed=await ErrEmbed(self, "Format incorect al duratei pedepsei!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

            role = disnake.utils.get(inter.guild.roles, name='Role Banned')
            if role in member.roles:
                return await inter.response.send_message(embed=await ErrEmbed(self, 'Utilizatorul are deja blocare pentru cererea de rol'), delete_after=DELETE_ERROR_SECONDS, ephemeral=True)
        
            punish = Punish(inter=inter, type='BANROLEREQUEST', member=member, reason=reason, duration=duration, endTime=await time_diff() + await convert_to_seconds(duration))
            try:
                await send_punish_response(self, inter, punish)
                await send_punish_dm(self, punish)

                await member.add_roles(role)

                await send_punish_log(self, punish)
                await self.bot.db.insert_punish(await punish.to_dict())
            except Exception as e:
                await inter.followup.send(e, ephemeral=True)

        else:
            orgroles = await getOrganizationalRoles(self, inter.guild.id)
            roleToRemove = None
            for role in member.roles:
                if role.id in orgroles:
                    roleToRemove = role
                    break
            if not roleToRemove:
                return await inter.response.send_message(embed=await ErrEmbed(self, "Nu au fost găsite roluri organizaționale pentru acest utilizator!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
            await member.remove_roles(roleToRemove)
            embed = disnake.Embed(title='Înlăturare roluri organizaționale', description=f'Rolul {role.mention} a fost îndepărtat de la utilizatorul {member.mention}', color=disnake.Colour.blue())
            if reason:
                embed.add_field(name='Motiv', value=f'{reason}')
            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
            await inter.response.send_message(embed=embed)

            data = {
                'type': 'ROLE_REMOVE',
                'guildId': inter.guild.id,
                'moderId': inter.author.id,
                'memberId': member.id,
                'reason': reason,
                'duration': None,
                'endTime': None,
                'timeNow': await time_diff(),
                'date': datetime.now().strftime("%d.%m.%Y")
            }

            await self.bot.db.insert_punish(data)

    @commands.slash_command(description='Trimite un mesaj pentru tichete')
    @commands.has_permissions(administrator=True)
    async def ticketmessage(self, inter: disnake.ApplicationCommandInteraction, channel: TextChannel):
        view = ticketCreateButton(bot=self.bot)
        embed = disnake.Embed(title='？Adresați o întrebare', description=f'**Aici puteți adresa întrebări agenților de suport referitoare la reguli sau comportament pe serverul Discord {inter.guild.name}**', colour=disnake.Colour.blue())
        embed.set_footer(text=inter.guild.name, icon_url=self.bot.user.display_avatar.url)
        await channel.send(embed=embed, view=view)
        await inter.response.send_message('Mesajul a fost trimis!', ephemeral=True)

    @commands.slash_command(description='Trimite un mesaj pentru atribuirea rolurilor')
    @commands.has_permissions(administrator=True)
    async def rolemessage(self, inter: disnake.ApplicationCommandInteraction, channel: TextChannel):
        stringSelect = RoleRequestDropDown(guildId=inter.guild.id)

        embed = disnake.Embed(title='**📨 | Cerere de rol**', description='Pentru a solicita un rol, selectează organizația ta din lista de mai jos.', colour=disnake.Colour.blue())
        embed.set_footer(text=inter.guild.name, icon_url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed, components=[stringSelect])
        await inter.response.send_message('Mesajul a fost trimis!', ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, inter: disnake.MessageInteraction):
        if isinstance(inter, disnake.ApplicationCommandInteraction):
            return
        if isinstance(inter, disnake.ModalInteraction):
            return

        if inter.component.custom_id == "RoleRequestDropDownId":
    # Creează instanța corectă a dropdown-ului
            stringSelect = RoleRequestDropDown(self.bot, guildId=inter.guild.id)
            await stringSelect.load_options()



            await inter.message.edit(components=[stringSelect])
            role = disnake.utils.get(inter.guild.roles, name='Role Banned')
            if role in inter.author.roles:
                return await inter.response.send_message(embed=await ErrEmbed(self, "Îți este blocată cererea de rol!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
        
            organizationalRoles = await getOrganizationalRoles(inter.guild.id)
            if not organizationalRoles:
                return await inter.response.send_message(embed=await ErrEmbed(self, "Sistemul de acordare a rolurilor nu este configurat!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            
            selected_value = inter.data.get("values")[0]
            for organizationalRole in organizationalRoles:
                if selected_value == organizationalRole[0]:
                    tag = organizationalRole[2]
                    selectedRoleId = organizationalRole[1]
                    context = await self.bot.db.get_context({'guildId': inter.guild.id, 'type': 'RoleRequest', 'memberId': inter.author.id})

                    if context:
                        return await inter.response.send_message(embed=await ErrEmbed(self, "Ai deja o cerere de rol deschisă, așteaptă să fie procesată!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

                    data = {
                        'type': 'RoleRequest',
                        'guildId': inter.guild.id,
                        'memberId': inter.author.id,
                        'tag': tag,
                        'roleId': selectedRoleId,
                        'messageId': None,
                    }

                    modal = RoleRequestModal(bot=self.bot, data=data)
                    await inter.response.send_modal(modal)
                    break

    @commands.slash_command(description='Acordă sau elimină puncte unui moderator')
    async def changestat(self, inter: disnake.ApplicationCommandInteraction,
                        member: disnake.Member=commands.Param(description='Utilizator (menționare sau id)', name='utilizator'), 
                        ball: int=commands.Param(description='Numărul de puncte', name='puncte'),
                        reason: str = commands.Param(description='Motivul', default='Nu este specificat')):

        if not await getBanAccess(self, inter.author):
            raise commands.MissingPermissions(['Acces la banare lipsă'])

        date = datetime.now().strftime("%d.%m.%Y")
        data = {
            'type': 'DELETE_BALL',
            'guildId': inter.guild.id,
            'moderId': member.id,
            'memberId': None,
            'reason': reason,
            'duration': ball,
            'timeNow': await time_diff(),
            'endTime': inter.author.id,
            'date': date
        }
        await self.bot.db.insert_punish(data)

        embed = disnake.Embed(title="[✅] Comandă executată cu succes!", description=f"**Moderatorului {member.mention} i-au fost acordate {ball} puncte!**", colour=disnake.Colour.green())
        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
        await inter.response.send_message(embed=embed, ephemeral=True)
        channel = await getModerationLogChannel(self, inter.guild.id)
        if channel:

            embed = disnake.Embed(title=f'Acordare puncte', colour=disnake.Colour.default())
            embed.add_field(name='A acordat', value=inter.author.mention, inline=True)
            embed.add_field(name='Moderator', value=member.mention, inline=True)
            embed.add_field(name='Puncte acordate', value=ball, inline=True)
            embed.add_field(name='Motiv', value=reason, inline=True)
            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

            await channel.send(embed=embed)

def setup(bot: CustomClient):
    bot.add_cog(Moderation(bot))
