import disnake

from Tools.GeneralUI import ErrEmbed
from Classes.CustomClient import CustomClient

class getModerStatButtonsEphemeralFalse(disnake.ui.View):
    def __init__(self, bot:CustomClient, data: list, author: disnake.Member, countMods: int, endPage: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.data = data
        self.author = author
        self.skip = 0
        self.countMods = countMods
        self.page = 1
        self.endPage = endPage

    @disnake.ui.button(emoji='◀️', style=disnake.ButtonStyle.blurple, custom_id='getModerStatLeft')
    async def button_1_callback(self, button:disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author == self.author:
            if self.page > 1:
                embed = inter.message.embeds[0]
                embed = disnake.Embed(title=embed.title, color = disnake.Colour.blue())
                self.skip -= 6
                self.page -= 1
                for item in self.data:
                    if self.skip + 6 >= item[0] > self.skip:
                        embed.add_field(name = item[2][1], value=item[3])
                embed.set_footer(text=f"Pagina {self.page} / {(self.countMods // 6) + 1 if self.countMods % 2 !=0 else self.countMods // 6}", icon_url=self.bot.user.display_avatar.url)
                await inter.response.edit_message(embed=embed)
            else:
                await inter.response.edit_message()
        else:
            await inter.response.send_message(embed=await ErrEmbed(self,f"Nu puteți interacționa cu această listă!\nInteracțiunea este disponibilă doar pentru {self.author.mention}"), ephemeral=True)

    @disnake.ui.button(emoji='🗑️', style=disnake.ButtonStyle.red, custom_id='getModerStatDelete')
    async def button_2_callback(self, button:disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author == self.author:
            await inter.message.delete()
        else:
            await inter.response.send_message(embed=await ErrEmbed(self,f"Nu puteți interacționa cu această listă!\nInteracțiunea este disponibilă doar pentru {self.author.mention}"), ephemeral=True)

    @disnake.ui.button(emoji='▶️', style=disnake.ButtonStyle.blurple, custom_id='getModerStatRight')
    async def button_3_callback(self, button:disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author == self.author:
            if self.page < self.endPage:
                embed = inter.message.embeds[0]
                embed = disnake.Embed(title=embed.title, color = disnake.Colour.blue())
                self.skip += 6
                self.page += 1
                for item in self.data:
                    if self.skip + 6 >= item[0] > self.skip:
                        embed.add_field(name = item[2][1], value=item[3])
                embed.set_footer(text=f"Pagina {self.page} / {(self.countMods // 6) + 1 if self.countMods % 2 !=0 else self.countMods // 6}", icon_url=self.bot.user.display_avatar.url)
                await inter.response.edit_message(embed=embed)
            else:
                await inter.response.edit_message()
        else:
            await inter.response.send_message(embed=await ErrEmbed(self,f"Nu puteți interacționa cu această listă!\nInteracțiunea este disponibilă doar pentru {self.author.mention}"), ephemeral=True)

class getModerStatButtonsEphemeralTrue(disnake.ui.View):
    def __init__(self, bot:CustomClient, data: list, author: disnake.Member, countMods: int, endPage: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.data = data
        self.author = author
        self.skip = 0
        self.countMods = countMods
        self.page = 1
        self.endPage = endPage

    @disnake.ui.button(emoji='◀️', style=disnake.ButtonStyle.blurple, custom_id='getModerStatLeft')
    async def button_1_callback(self, button:disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author == self.author:
            if self.page > 1:
                embed = inter.message.embeds[0]
                embed = disnake.Embed(title=embed.title, color = disnake.Colour.blue())
                self.skip -= 6
                self.page -= 1
                for item in self.data:
                    if self.skip + 6 >= item[0] > self.skip:
                        embed.add_field(name = item[2][1], value=item[3])
                embed.set_footer(text=f"Pagina {self.page} / {(self.countMods // 6) + 1 if self.countMods % 2 !=0 else self.countMods // 6}", icon_url=self.bot.user.display_avatar.url)
                await inter.response.edit_message(embed=embed)
            else:
                await inter.response.edit_message()
        else:
            await inter.response.send_message(embed=await ErrEmbed(self,f"Nu puteți interacționa cu această listă!\nInteracțiunea este disponibilă doar pentru {self.author.mention}"), ephemeral=True)

    @disnake.ui.button(emoji='▶️', style=disnake.ButtonStyle.blurple, custom_id='getModerStatRight')
    async def button_3_callback(self, button:disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author == self.author:
            if self.page < self.endPage:
                embed = inter.message.embeds[0]
                embed = disnake.Embed(title=embed.title, color = disnake.Colour.blue())
                self.skip += 6
                self.page += 1
                for item in self.data:
                    if self.skip + 6 >= item[0] > self.skip:
                        embed.add_field(name = item[2][1], value=item[3])
                embed.set_footer(text=f"Pagina {self.page} / {(self.countMods // 6) + 1 if self.countMods % 2 !=0 else self.countMods // 6}", icon_url=self.bot.user.display_avatar.url)
                await inter.response.edit_message(embed=embed)
            else:
                await inter.response.edit_message()
        else:
            await inter.response.send_message(embed=await ErrEmbed(self,f"Nu puteți interacționa cu această listă!\nInteracțiunea este disponibilă doar pentru {self.author.mention}"), ephemeral=True)
