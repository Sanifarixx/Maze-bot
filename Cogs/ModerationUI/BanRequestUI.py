import disnake
from datetime import datetime


from config import DELETE_ERROR_SECONDS
from Tools.Get.Access import getBanAccess
from Tools.Get.Check import check_punish_duration_format
from Tools.GeneralUI import ErrEmbed
from Tools.Get.Log import getModerationLogChannel
from Tools.Get.Different import time_diff, convert_to_seconds
from Classes.CustomClient import CustomClient

class banRequestButtons(disnake.ui.View):
    def __init__(self, bot: CustomClient):
        super().__init__(timeout=None)
        self.bot = bot
    
    @disnake.ui.button(emoji="✔️", style=disnake.ButtonStyle.green, custom_id="banRequestAccept")
    async def button_1_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if await getBanAccess(self, inter.author): 

            embed = inter.message.embeds[0]
            user = await self.bot.fetch_user(int(embed.fields[0].value[2:-1]))
            moder = await self.bot.fetch_user(int(embed.fields[1].value[2:-1]))
            reason = embed.fields[3].value
            duration = embed.fields[2].value
            embed.add_field(name='Formular aprobat', value=f'{inter.author.mention}', inline=False)
            embed.colour = disnake.Colour.green()

            self.button_1_callback.disabled = True
            self.button_2_callback.disabled = True

            await inter.response.edit_message(content='', embed=embed, view=self)

            endTime = await time_diff() + await convert_to_seconds(duration)

            channel = await getModerationLogChannel(self, inter.guild.id)
            if channel:

                embed = disnake.Embed(title=f'[BAN] {user.display_name}', colour=disnake.Colour.default(),) 
                embed.add_field(name='Moderator', value= moder.mention, inline=True)
                embed.add_field(name='Utilizator', value= user.mention, inline=True)
                embed.add_field(name='Motiv', value=f'{reason}', inline=True)
                embed.add_field(name='Durata sancțiunii', value= duration, inline=True)
                embed.add_field(name='Data finalizării sancțiunii', value=f'<t:{endTime}>', inline=True)
                embed.add_field(name='Aprobat de', value=f'{inter.author.mention}', inline=False)
                embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                await channel.send(embed=embed)

            embed = disnake.Embed(title='[✅] Realizat cu succes!', colour=disnake.Colour.brand_green(), description=f'**Ai acceptat [formularul](https://discord.com/channels/{inter.guild.id}/{inter.channel.id}/{inter.message.id})**')
            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

            await inter.send(embed=embed, ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

            date = datetime.now().strftime("%d.%m.%Y")

            userData = {
                'type': 'BAN',
                'guildId': inter.guild.id,
                'moderId': moder.id,
                'memberId': user.id,
                'reason': reason,
                'duration': duration,
                'endTime': endTime,
                'timeNow': await time_diff(),
                'date': date
            }

            moderData = {
                'type': 'FORM_ACCEPT',
                'guildId': inter.guild.id,
                'moderId': inter.author.id,
                'memberId': moder.id,
                'reason': reason,
                'duration': None,
                'endTime': None,
                'timeNow': await time_diff(),
                'date': date
            }

            await self.bot.db.insert_punish(moderData)
            await self.bot.db.insert_punish(userData)


            embed = disnake.Embed(title=f'Ai fost banat de pe serverul {inter.guild.name}', description=f'Moderator:`{moder.display_name} [{moder.id}]`'
                                                                                            f'\nMotiv:`{reason}`'
                                                                                            f'\nData finalizării sancțiunii:<t:{await time_diff() + await convert_to_seconds(duration)}>',
            colour=disnake.Colour.red(),)
            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

            try:
                await user.send(embed=embed) 
            except:
                pass

            await inter.guild.ban(user=user, reason=reason)   

    @disnake.ui.button(emoji="✖️", style=disnake.ButtonStyle.red, custom_id="banRequestDecline")
    async def button_2_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if await getBanAccess(self, inter.author):      

            embed = inter.message.embeds[0]
            moder = await self.bot.fetch_user(int(embed.fields[1].value[2:-1]))
            reason = embed.fields[3].value
            embed.add_field(name='Formular respins', value= inter.author.mention, inline=False)
            embed.colour = disnake.Colour.red()

            self.button_1_callback.disabled = True
            self.button_2_callback.disabled = True

            await inter.response.edit_message(content='', embed=embed, view=self)

            date = datetime.now().strftime("%d.%m.%Y")

            data = {
                'type': 'FORM_REJECT',
                'guildId': inter.guild.id,
                'moderId': inter.author.id,
                'memberId': moder.id,
                'reason': reason,
                'duration': None,
                'endTime': None,
                'timeNow': await time_diff(),
                'date': date
            }

            await self.bot.db.insert_punish(data)

            embed = disnake.Embed(title='[✅] Realizat cu succes!', colour=disnake.Colour.brand_red(), description=f'**Ai respins [formularul](https://discord.com/channels/{inter.guild.id}/{inter.channel.id}/{inter.message.id})**')
            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

            await inter.send(embed=embed, ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

class banRequestModal(disnake.ui.Modal):
    def __init__(self, bot: CustomClient, member):
        self.member = member
        components=[
            disnake.ui.TextInput(
                label="Durata sancțiunii s/m/d/w",
                placeholder="",
                custom_id="Durata blocării",
                style=disnake.TextInputStyle.short,
                max_length=5,
            ),
            disnake.ui.TextInput(
                label="Motiv",
                placeholder="",
                custom_id="Motiv",
                style=disnake.TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Dovezi",
                placeholder="",
                custom_id="Dovezi",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
        ]

        super().__init__(
            title="Trimite formular pentru ban",
            custom_id="banRequestModal",
            components=components,
        )
        self.bot = bot

    async def callback(self, inter: disnake.ModalInteraction):

        if await check_punish_duration_format(inter.text_values["Durata blocării"]):

            embed = disnake.Embed(title="Formular | Ban", colour=disnake.Colour.yellow(),)
            embed.add_field(name='Utilizator', value= self.member.mention, inline=True)
            embed.add_field(name='Moderator', value= inter.author.mention, inline=True)
            embed.add_field(name='Durata blocării', value=inter.text_values['Durata blocării'], inline=True)
            embed.add_field(name='Motiv', value=inter.text_values['Motiv'], inline=False)
            embed.add_field(name='Dovezi', value=inter.text_values['Dovezi'], inline=True)

            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

            config = await self.bot.db.get_config(inter.guild.id)
            if config['banRequestChannel']:

                view = banRequestButtons(bot=self.bot)
                channel = self.bot.get_channel(config['banRequestChannel'])
                if channel:
                    if config['banRequestRole']:
                        message123 = await channel.send(f"<@&{config['banRequestRole']}>", embed=embed, view=view)
                    else:
                        message123 = await channel.send(embed=embed, view=view)

                    embed = disnake.Embed(title='Formular trimis', colour=disnake.Colour.dark_green(), description=f'**[Formular](https://discord.com/channels/{inter.guild.id}/{channel.id}/{message123.id}) a fost trimis cu succes!**')

                    await inter.response.send_message(embed=embed, ephemeral=True, delete_after=10)
                else:
                    await inter.response.send_message(embed=await ErrEmbed(self, "Canalul pentru trimiterea formularului nu este configurat!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
            else:
                await inter.response.send_message(embed=await ErrEmbed(self, "Canalul pentru trimiterea formularului nu este configurat!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS) 
        else:
            await inter.response.send_message(embed=await ErrEmbed(self, "Format incorect al duratei sancțiunii!"), ephemeral=True, delete_after=DELETE_ERROR_SECONDS)
