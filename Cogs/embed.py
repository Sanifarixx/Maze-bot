import disnake
from disnake.ext import commands
from disnake import TextChannel
import datetime

def admin_check(member: disnake.Member):
  if member.guild_permissions.administrator:
    return True
  else:
    return False

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generatedEmbed = disnake.Embed()

    @commands.slash_command(description='Создание embed')
    async def embed(self, inter):
        pass

    @embed.sub_command(name="add_field", description="Добавить поле в embed")
    async def add_field(self, inter:disnake.ApplicationCommandInteraction, name: str = commands.Param(description='Заголовок поля', default=''), value: str = commands.Param(description='Текст поля (для переноса по строкам - символ | )'), inline: bool = commands.Param(default=True | False, description='В одной строке?')):
        if admin_check(inter.author):
            value_lines = value.split('|')
            formatted_value = '\n'.join(value_lines)
            self.generatedEmbed.add_field(name=name, value=formatted_value, inline=inline)
            embed1 = disnake.Embed(description='**Поле успешно добавлено!**', colour = disnake.Colour.green(),)
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)

    @embed.sub_command(name="colour", description="Установить цвет embed")
    async def colour(self, inter:disnake.ApplicationCommandInteraction, color: disnake.Color = commands.Param(description='Цвет формата #код')):
        if admin_check(inter.author):
            self.generatedEmbed = color
            embed1 = disnake.Embed(description=f'**Цвет успешно добавлен!**', colour=disnake.Colour.green(),)
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)

    @embed.sub_command(name="author", description="Установить автора embed")
    async def set_author(self, inter:disnake.ApplicationCommandInteraction, name: str, icon_url: str = None):
        if admin_check(inter.author):
            if icon_url:
                self.generatedEmbed.set_author(name=name, icon_url=icon_url)
            else:
                self.generatedEmbed.set_author(name=name)
            embed1 = disnake.Embed(description=f"**Автор успешно добавлен**", colour=disnake.Colour.green(),)
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)

    @embed.sub_command(name="footer", description="установить текст нижнего колонтитула ")
    async def set_footer(self, inter:disnake.ApplicationCommandInteraction, text: str, icon_url: str = commands.Param(default=None, description='Ссылка на изображение')):
        if admin_check(inter.author):
            if icon_url:
                self.generatedEmbed.set_footer(text=text, icon_url=icon_url)
            else:
                self.generatedEmbed.set_footer(text=text)
            embed1 = disnake.Embed(description=f"**Текст нижнего колонтитула успешно установлен!**", colour=disnake.Colour.green(),)
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)

    @embed.sub_command(name="description", description="Установить описание embed")
    async def description(self, inter:disnake.ApplicationCommandInteraction, description: str = commands.Param(description='Для разделения текста по строкам - символ |')):
        if admin_check(inter.author):
            value_lines = description.split('|')
            formatted_value = '\n'.join(value_lines)
            self.generatedEmbed.description = formatted_value
            embed1 = disnake.Embed(description='**Описание успешно добавлено**', colour = disnake.Colour.green())
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)

    @embed.sub_command(name="title", description="Установить заголовок embed")
    async def title(self, inter:disnake.ApplicationCommandInteraction, title: str):
        if admin_check(inter.author):
            self.generatedEmbed.title = title
            embed1 = disnake.Embed(description='**Заголовок успешно добавлен!**', colour = disnake.Colour.green())
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)

    @embed.sub_command(name='send', description="Отправить embed")
    @commands.has_permissions(administrator=True)
    async def send(self, inter:disnake.ApplicationCommandInteraction, channel: TextChannel = commands.Param(description='id или упоминание канала для отправки')):
        try:
            await channel.send(embed=self.generatedEmbed)
            embed1 = disnake.Embed(description='**Сообщение успешно отправлено!**', colour = disnake.Colour.green())
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5)
            self.generatedEmbed = disnake.Embed()
        except:
            await inter.response.send_message("Произошла ошибка при отправке сообщения!", ephemeral=True)

    @embed.sub_command(name='image', description="Добавить изображение в embed")
    async def addimage(self, inter:disnake.ApplicationCommandInteraction, image:str = commands.Param(description='Ссылка на изображение')):
        if admin_check(inter.author):
            self.generatedEmbed.set_image(url = image)
            embed1 = disnake.Embed(description='**Изображение успешно добавлено!**', colour = disnake.Colour.green())
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5 )

    @embed.sub_command(name='help', description="Помощь в создании embed")
    async def help(self, inter:disnake.ApplicationCommandInteraction):
        if admin_check(inter.author):
            embed1 = disnake.Embed(title = 'Помощь в создании embed', description='', colour = disnake.Colour.yellow())
            await inter.response.send_message(embed=embed1 )

    @embed.sub_command(name='reset', description="Сбросить embed")
    async def reset(self, inter:disnake.ApplicationCommandInteraction):
        if admin_check(inter.author):
            self.generatedEmbed = disnake.Embed()
            embed = disnake.Embed(description='**Embed успешно сброшен**', colour = disnake.Colour.green())
            await inter.response.send_message(embed=embed, ephemeral=True, delete_after=5 )

    @embed.sub_command(name='timestamp', description="Добавить timestamp")
    async def timestamp(self, inter:disnake.ApplicationCommandInteraction):
        if admin_check(inter.author):
            self.generatedEmbed.timestamp = datetime.datetime.now()
            embed1 = disnake.Embed(description='**Timestamp успешно добавлен**', colour = disnake.Colour.green())
            await inter.response.send_message(embed=embed1, ephemeral=True, delete_after=5 )

    @embed.sub_command(name='preview', description="Посмотреть созданный embed")
    async def preview(self, inter:disnake.ApplicationCommandInteraction, ephemeral:bool = True | False):
        if admin_check(inter.author):
            try:
                await inter.response.send_message(embed=self.generatedEmbed, ephemeral=ephemeral)
            except:
                await inter.response.send_message("Произошла ошибка при отправке сообщения!", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(EmbedBuilder(bot))