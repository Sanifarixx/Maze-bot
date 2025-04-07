import disnake
from datetime import datetime

from Tools.Get.Different import time_diff, convert_to_seconds
from Tools.Get.Access import getModerAccess
from config import DELETE_ERROR_SECONDS
from Classes.CustomClient import CustomClient

class notifyDropDown(disnake.ui.StringSelect):
    def __init__(self, bot: CustomClient, reason, duration, author, member: disnake.Member):
        self.reason=reason
        self.duration=duration
        self.author=author
        self.member = member
        options=[
            disnake.SelectOption(label="Avatar"),
            disnake.SelectOption(label="Descriere"),
            disnake.SelectOption(label="Despre mine"),
            disnake.SelectOption(label="Status"),
            disnake.SelectOption(label="Banner"),
            disnake.SelectOption(label="Nickname"),
        ]

        super().__init__(
            custom_id='notifyDropDown',
            placeholder="Selectați partea de profil dorită",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.bot=bot
    
    async def callback(self, inter: disnake.MessageInteraction):
        config = await self.bot.db.get_config(inter.guild.id)
        if config['notifychannel']:
            channel = self.bot.get_channel(config['notifychannel'])
            if channel:

                embed=disnake.Embed(title='Notificare despre încălcarea profilului', description=f'Punctul din reguli:', colour=disnake.Colour.blue(),)
                embed.add_field(name='', value=f'```{self.reason}```', inline=False)
                embed.add_field(name='', value=f'Schimbați `{self.values[0]}`, în caz contrar veți fi sancționat.', inline=False)

                embed.add_field(name='', value=f'\nNotificarea va expira <t:{await time_diff() + await convert_to_seconds(self.duration)}:R>.' 
                                             f'\nAți fost notificat de {self.author.mention}',
                            inline=False)
                embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

                view = notifyCancelButton(bot = self.bot)
                message=await channel.send(self.member.mention, embed=embed, view=view)

                embed=disnake.Embed(title='Notificare', description=f'**[Notificarea](https://discord.com/channels/{inter.guild.id}/{channel.id}/{message.id}) a fost trimisă cu succes!**', color=disnake.Colour.green())
                embed.set_footer(text=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)

                await inter.response.send_message(embed=embed, ephemeral=True, delete_after=DELETE_ERROR_SECONDS)

                endTime = await time_diff() + await convert_to_seconds(self.duration)

                date=datetime.now().strftime("%d.%m.%Y")

                data = {
                    'type': 'NOTIFY',
                    'guildId': inter.guild.id,
                    'moderId': inter.author.id,
                    'memberId': self.member.id,
                    'reason': None,
                    'duration': None,
                    'timeNow': await time_diff(),
                    'endTime': endTime,
                    'date': date,
                    'notifyMessageId': message.id
                }

                await self.bot.db.insert_punish(data)

            else:
                await inter.response.send_message('Sistemul de notificări nu este configurat!', ephemeral=True)
        else:
            await inter.response.send_message('Sistemul de notificări nu este configurat!', ephemeral=True)

class notifyDropDownView(disnake.ui.View):
    def __init__(self, bot, reason, duration, author, member):
        super().__init__(timeout=None)
        self.add_item(notifyDropDown(bot, reason, duration, author, member))

class notifyCancelButton(disnake.ui.View):
    def __init__(self, bot: CustomClient):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(emoji='🛑',label="Anulează notificarea", style=disnake.ButtonStyle.red, custom_id="notifydisable")
    async def button_1_callback(self, button:disnake.ui.Button, interaction: disnake.MessageInteraction):
            if interaction.component.custom_id=="notifydisable":
                if await getModerAccess(self, interaction.author):
                    await interaction.response.edit_message()
                    await  interaction.message.delete()

                    await self.bot.db.delete_punish({'notifyMessageId': interaction.message.id})
