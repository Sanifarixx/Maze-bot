import disnake
from datetime import datetime

from config import DELETE_ERROR_SECONDS
from Tools.Get.Access import getModerAccess
from Tools.GeneralUI import ErrEmbed
from Tools.Get.Log import getTicketLogChannel
from Tools.Get.Different import convert_to_seconds, time_diff
from Classes.CustomClient import CustomClient

class ticketButtons(disnake.ui.View):
    def __init__(self, bot: CustomClient):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(emoji="🔐", style=disnake.ButtonStyle.grey, custom_id=f'pinTicket')
    async def pin(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if await getModerAccess(self, inter.author):

            config = await self.bot.db.get_config(inter.guild.id)

            if config['ticketzakrep']:
                category = disnake.utils.get(inter.guild.categories, id=config['ticketzakrep'])
                if category:
                    if inter.channel.category != category:
                        await inter.channel.edit(category=category)
                        embed = disnake.Embed(title='🔐 ❘ Fixarea unui ticket', description=f'Moderatorul {inter.author.mention} a fixat un ticket.', colour=disnake.Colour.orange(),)
                        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)              
                        await inter.response.edit_message()
                        await inter.channel.send(embed=embed)

                        channel = await getTicketLogChannel(self, inter.guild.id)
                        if channel:
                            embed = disnake.Embed(title='🔐 ❘ Fixarea unui ticket', colour=disnake.Colour.orange(),)
                            embed.add_field(name='Moderator', value=f'{inter.author.mention}', inline=True)
                            embed.add_field(name='Ticket', value=f'{inter.channel.mention}`{inter.channel.name}`', inline=True)
                            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                            await channel.send(embed=embed)
                    else:
                        await inter.response.send_message(embed=await ErrEmbed(self, "Ticket-ul este deja fixat!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
                else:
                    await inter.response.send_message(embed=await ErrEmbed(self, "Categorii pentru tickete nu sunt configurate!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            else:
                await inter.response.send_message(embed=await ErrEmbed(self, "Categorii pentru tickete nu sunt configurate!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

    @disnake.ui.button(emoji="🔒", style=disnake.ButtonStyle.grey, custom_id=f'closeTicket')
    async def close(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if await getModerAccess(self, inter.author):
            role = disnake.utils.get(inter.guild.roles, name='@everyone')
            if inter.channel.permissions_for(role).send_messages:
                config = await self.bot.db.get_config(inter.guild.id)

                if config['ticketclose']:
                    category = disnake.utils.get(inter.guild.categories, id=config['ticketclose'])
                    if category:
                        await inter.channel.edit(category=category)

                        embed = disnake.Embed(title='🔒 ❘ Închiderea unui ticket', description=f'Moderatorul {inter.author.mention} a închis un ticket.', colour=disnake.Colour.red(),)
                        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                        await inter.response.edit_message()

                        await inter.channel.send(embed=embed)

                        channel = await getTicketLogChannel(self, inter.guild.id)
                        if channel:
                            embed = disnake.Embed(title='🔒 ❘ Închiderea unui ticket', colour=disnake.Colour.red(), timestamp=disnake.utils.utcnow())
                            embed.add_field(name='Moderator', value=f'{inter.author.mention}', inline=True)
                            embed.add_field(name='Ticket', value=f'{inter.channel.mention}`{inter.channel.name}`', inline=True)
                            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                            await channel.send(embed=embed)

                        role = disnake.utils.get(inter.guild.roles, name='@everyone')
                        await inter.channel.set_permissions(role, send_messages=False, view_channel=False)  
                        
                        punish = await self.bot.db.get_punish({'memberId': inter.channel.id})
                        if not punish:
                            date = datetime.now().strftime("%d.%m.%Y")
                            endTime = await time_diff() + await convert_to_seconds('1d') 
                            data = {
                                'type': 'TICKET',
                                'guildId': inter.guild.id,
                                'moderId': inter.author.id,
                                'memberId': inter.channel.id,
                                'reason': None,
                                'duration': None,
                                'timeNow': await time_diff(),
                                'endTime': endTime,
                                'date': date
                            }
                            await self.bot.db.insert_punish(data)
                    else:
                        await inter.response.send_message(embed=await ErrEmbed(self, "Categorii pentru tickete nu sunt configurate!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
                else:
                    await inter.response.send_message(embed=await ErrEmbed(self, "Categorii pentru tickete nu sunt configurate!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            else:
                await inter.response.send_message(embed=await ErrEmbed(self, "Ticket-ul este deja închis!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

    @disnake.ui.button(emoji="📂", style=disnake.ButtonStyle.grey, custom_id=f'openTicket')
    async def open(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if await getModerAccess(self, inter.author):
            role = disnake.utils.get(inter.guild.roles, name='@everyone')
            if not inter.channel.permissions_for(role).send_messages:
                await inter.response.edit_message()

                embed = disnake.Embed(title='📂 ❘ Deschiderea unui ticket', description=f'Moderatorul {inter.author.mention} a deschis un ticket.', colour=disnake.Colour.blue(),)
                embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                await inter.channel.send(embed=embed)  

                channel = await getTicketLogChannel(self, inter.guild.id)      
                if channel: 
                    embed = disnake.Embed(title='📂 ❘ Deschiderea unui ticket', colour=disnake.Colour.blue(), timestamp=disnake.utils.utcnow())
                    embed.add_field(name='Moderator', value=f'{inter.author.mention}', inline=True)
                    embed.add_field(name='Ticket', value=f'{inter.channel.mention}`{inter.channel.name}`', inline=True)
                    embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
                    await channel.send(embed=embed)
                    
                await inter.channel.set_permissions(role, send_messages=True)
                
                await self.bot.db.delete_context({'memberId': inter.channel.id})
            else:
                await inter.response.send_message(embed=await ErrEmbed(self, "Ticket-ul este deja deschis!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

class ticketCreateButton(disnake.ui.View):
    def __init__(self, bot: CustomClient):
        super().__init__(timeout=None)
        self.bot = bot
        
    @disnake.ui.button(emoji="✏️", label='Adresează o întrebare', style=disnake.ButtonStyle.blurple, custom_id=f'createticket')
    async def callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        role = disnake.utils.get(inter.guild.roles, name='Ticket Banned')
        if not role or not (role in inter.author.roles):

            config = await self.bot.db.get_config(inter.guild.id)

            if config['ticketactive'] and config['ticketclose'] and config['ticketzakrep']:

                category = disnake.utils.get(inter.guild.categories, id=config['ticketactive'])
                if category:
                    await self.bot.db.update_config(inter.guild.id, {'ticketcount': config['ticketcount'] + 1})
                    ticketChannel = await inter.guild.create_text_channel(f"ticket-{config['ticketcount']}", category=category)
                    await ticketChannel.set_permissions(inter.author, view_channel=True)  

                    embed = disnake.Embed(title='Crearea unui ticket', description=f'Ticket-ul {ticketChannel.mention} a fost creat! ', colour=disnake.Colour.dark_magenta(),)
                    embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                    await inter.response.send_message(embed=embed, ephemeral=True, delete_after=30)
                    
                    embed = disnake.Embed(title='Ticket nou', description='Stimate utilizator! În caz de reclamații referitoare la activitatea moderatorilor, vă puteți adresa administrației.', colour=disnake.Colour.green(),) 

                    embed.set_author(name=f'{inter.author.display_name}', icon_url=inter.author.avatar.url if inter.author.avatar else inter.author.default_avatar.url)

                    
                    view = ticketButtons(bot=self.bot)
                    if config['ticketrole']:
                        await ticketChannel.send(f"<@&{config['ticketrole']}>", embed=embed, view=view)
                    else:
                        await ticketChannel.send(embed=embed, view=view)

                    channel = await getTicketLogChannel(self, inter.guild.id)
                    if channel:
                        embed = disnake.Embed(title='🎟 ❘ Crearea unui ticket', colour=disnake.Colour.green(), timestamp=disnake.utils.utcnow())
                        embed.add_field(name='Utilizator', value=f'{inter.author.mention}', inline=True)
                        embed.add_field(name='Ticket', value=f'{ticketChannel.mention}`{ticketChannel.name}`', inline=True)
                        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                        await channel.send(embed=embed)
                else:
                    await inter.response.send_message(embed=await ErrEmbed(self, "Categorii pentru tickete nu sunt configurate!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            else:
                await inter.response.send_message(embed=await ErrEmbed(self, "Categorii pentru tickete nu sunt configurate!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)    
        else:
            await inter.response.send_message(embed=await ErrEmbed(self, "Aveți blocare pentru tickete!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
