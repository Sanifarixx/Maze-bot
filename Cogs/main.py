import disnake
from disnake.ext import commands
import asyncio
from datetime import datetime

from Classes.CustomClient import CustomClient
from Tools.Get.Log import privateRoomsLog
from Tools.GeneralUI import ErrEmbed
from Tools.dbTemplates.Templates import CONFIG_TEMPLATE

async def handle_join(self, member: disnake.Member, channel: disnake.VoiceChannel):
    result = await self.bot.db.get_context({"memberId": member.id, "type": "privateRoom"})
    if not result:

        category = channel.category
        room = await category.create_voice_channel(name=member.display_name)
        await room.set_permissions(member, manage_channels=True, move_members=True)
        await member.move_to(room)

        channel1 = await privateRoomsLog(self, member.guild.id)

        if channel1:

            embed = disnake.Embed(title="Crearea camerei private", color = disnake.Colour.green(), timestamp=disnake.utils.utcnow())
            embed.add_field(name="Camera", value=f"{room.mention}`{room.id}`", inline=False)
            embed.add_field(name="Proprietar", value=f"{member.mention}`{member.id}`", inline=False)
            embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
            await channel1.send(embed=embed)

        data = {
            "channelId": room.id,
            "memberId": member.id,
            "type": "privateRoom"
        }

        await self.bot.db.insert_context(data)

    else:
        await member.move_to(None)

async def handle_leave(self, channel: disnake.TextChannel):
        if len(channel.members) == 0:
            result = await self.bot.db.get_context({"channelId": channel.id})
            await self.bot.db.delete_context({"channelId": channel.id})

            member = channel.guild.get_member(result["memberId"])

            channel1 = await privateRoomsLog(self, member.guild.id)

            if channel1:

                embed = disnake.Embed(title="Ștergerea camerei private", color = disnake.Colour.red(), timestamp=disnake.utils.utcnow())
                embed.add_field(name="Camera", value=f"{channel.name}`{channel.id}`", inline = False)
                embed.add_field(name="Proprietar", value=f"{member.mention}`{member.id}`", inline = False)
                embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                await channel1.send(embed=embed)

            try:
                await channel.delete()
            except:
                pass

class Main(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if not message.author.bot and message.channel.id == 1311418426572406894:
            data = {
                "guildId": message.guild.id,
                'memberId': message.author.id,
                "id": message.id,
                "channelId": message.channel.id,
                'date': datetime.now().strftime("%d.%m.%Y")
            }
            await self.bot.db.insert_message(data)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        await self.bot.db.delete_message({"id": message.id})
        if message.embeds != []:

            if message.embeds[0].title == '**📨 | Cerere de rol**':
                await self.bot.db.delete_context({'messageId': message.id})

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):

            result = await self.bot.db.get_config(member.guild.id)
            if result:
                if result["privateRoom"]:
                    room = self.bot.get_channel(result["privateRoom"])
                else:
                    room = None
            else:
                room = None
            if room and after.channel and after.channel.category == room.category and after.channel == room:
                await handle_join(self, member, after.channel)
            if room and before.channel and before.channel != room and before.channel.category == room.category and before.channel != room:
                await handle_leave(self, before.channel)

    @commands.slash_command(description="Reîncărcarea modulului")
    @commands.has_permissions(administrator=True)
    async def dev_reload(self, inter:disnake.ApplicationCommandInteraction, cog_name: str):
        try:
            self.bot.reload_extension(f"Cogs.{cog_name}")
            await inter.response.send_message(f"Modulul {cog_name} a fost reîncărcat!", ephemeral=True, delete_after=10)
        except Exception as e:
            await inter.response.send_message(f"Eroare la reîncărcarea modulului {cog_name}: {e}", ephemeral=True)

    @commands.slash_command( description="Afișează lista modulelor încărcate.")
    @commands.has_permissions(administrator=True)
    async def dev_cogs(self, inter: disnake.ApplicationCommandInteraction):
        extensions = list(self.bot.extensions)
        if extensions:
            await inter.response.send_message(f"Module încărcate:\n```\n{''.join(extensions)}\n```", ephemeral=True)

        else:
            await inter.response.send_message("Nu sunt module încărcate.", ephemeral=True, delete_after=10)

    @commands.slash_command(description="Creează configurația serverului")
    @commands.has_permissions(administrator=True)
    async def config (self, inter:disnake.ApplicationCommandInteraction,
                      privateroom: disnake.VoiceChannel = commands.Param(name="camere_private", description="Canal pentru crearea camerelor private", default=None),
                      privateroomlog:disnake.TextChannel = commands.Param(name="log", description="Canal pentru logarea camerelor private", default=None)):
        
        embed = disnake.Embed(description="Modificări:", color = disnake.Colour.green(), timestamp=disnake.utils.utcnow())
        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

        searchConfig = await self.bot.db.get_config(inter.guild.id)
        if not searchConfig:
            data = CONFIG_TEMPLATE
            data['guildId'] = inter.guild.id

            await self.bot.db.insert_config(data)
            embed.description = "**Configurația serverului a fost creată**!"

        if privateroom:
            await self.bot.db.update_config(inter.guild.id, {"privateRoom": privateroom.id})

            embed.add_field(name="Canal pentru crearea camerelor private", value=privateroom.mention)

        if privateroomlog:
            await self.bot.db.update_config(inter.guild.id, {"privateRoomLog": privateroomlog.id})

            embed.add_field(name="Canal pentru logarea camerelor private", value=privateroomlog.mention)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(description="Informații despre configurația serverului")
    @commands.has_permissions(administrator=True)
    async def config_info(self, inter:disnake.ApplicationCommandInteraction):
            result = await self.bot.db.get_config(inter.guild.id)

            if result:
                embed = disnake.Embed(title=f"Serverul {inter.guild.name}", description=f'\n\n**Camere private:**\nCanal pentru camere private: <#{result["privateRoom"]}>\nCanal pentru logare: <#{result["privateRoomLog"]}>\n\n**Moderare:**\nCanal pentru logare:  <#{result["moderationLog"]}>\nRole de moderare: {[f"<@&{roleId}>" for roleId in result["moderPermRoles"]]}\nRole cu permisiune de ban: {[f"<@&{roleId}>" for roleId in result["banPermRoles"]]}\nCanal pentru trimiterea formularelor de ban: <#{result["banRequestChannel"]}>\nRolul care este notificat la trimiterea unui formular de ban: <@&{result["banRequestRole"]}>\nCanal pentru trimiterea /notify: <#{result["notifychannel"]}>\nCanal pentru notificarea moderatorilor: <#{result["notifynotifychannel"]}>\n\n**Tichete:**\nCanal pentru logarea tichete: <#{result["ticketLog"]}>\nRolul notificat la crearea unui tichet: <@&{result["ticketrole"]}>\nCategoria pentru tichete active: {result["ticketactive"]}\nCategoria pentru tichete închise: {result["ticketclose"]}\n\n**Puncte pentru sancțiuni:**\n\nCanal pentru numărarea mesajelor: <#{result["normachannel"]}>\nRolul pentru numărarea în /getmoderstat: <@&{result["normarole"]}>\n\nMuta: {result["ballmute"]}\nBan: {result["ballban"]}\nÎnchiderea tichetului: {result["ballticket"]}\nKick: {result["ballkick"]}\nBlocarea tichetelor: {result["ballticketban"]}\nAcceptarea formularului: {result["ballformaccept"]}\nRespinge formularul: {result["ballformreject"]}\nMute Voice: {result["ballvmute"]}\nMesaj: {result["ballmessage"]}')
                embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                await inter.response.send_message(embed=embed, ephemeral=True)
            else:
                await inter.response.send_message("Configurația serverului nu a fost găsită, folosește comanda /config", ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.TextChannel):
            await asyncio.sleep(5)
            result = await self.bot.db.get_context({'channelId': channel.id, 'type': 'privateRoom'})
            if result:
                member = channel.guild.get_member(result["memberId"])

                channel1 = await privateRoomsLog(self, member.guild.id)
                if channel1:

                    embed = disnake.Embed(title="Ștergerea camerei private", color = disnake.Colour.red(), timestamp=disnake.utils.utcnow())
                    embed.add_field(name="Camera", value=f"{channel.name}`{channel.id}`", inline = False)
                    embed.add_field(name="Proprietar", value=f"{member.mention}`{member.id}`", inline = False)
                    embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                    await channel1.send(embed=embed)

                await self.bot.db.delete_context({"channelId": channel.id, "type": "privateRoom"})

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: disnake.VoiceChannel, after: disnake.VoiceChannel):

        result = await self.bot.db.get_config(after.guild.id)

        if result:
            room = self.bot.get_channel(result['privateRoom'])

            if room:
                if after.category == room.category:
                    channel1 = await privateRoomsLog(self, after.guild.id)
                    if channel1:
                        embed = disnake.Embed(title='Modificarea camerei private', color = disnake.Colour.blue(), timestamp=disnake.utils.utcnow())
                        embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)

                        if before.name != after.name:
                            embed.add_field(name='Nume', value=f'{before.name} -> {after.name}', inline=False)
                        
                        if before.bitrate != after.bitrate:
                            embed.add_field(name='Bitrate', value=f'{before.bitrate} -> {after.bitrate}', inline=False)

                        if before.user_limit != after.user_limit:
                            embed.add_field(name='Limita', value=f'{before.user_limit} -> {after.user_limit}', inline=False)
                        
                        await channel1.send(embed=embed)

    @commands.Cog.listener()
    async def on_slash_command_error(self, interaction: disnake.Interaction, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(embed=await ErrEmbed(self,
                f"Nu atât de repede. Veți putea utiliza din nou această comandă după {error.retry_after:.2f} secunde"), ephemeral=True)

        elif isinstance(error, commands.BotMissingPermissions):
            interaction.application_id
            await interaction.response.send_message(embed=await ErrEmbed(self,
                f"Nu pot executa această comandă pentru că nu am permisiunile necesare, și anume: "
                f"`{' '.join(error.missing_permissions)}`"), ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(
                embed=await ErrEmbed(self, text = f"Nu aveți permisiunile necesare pentru a utiliza această comandă."), ephemeral=True)
        elif isinstance(error, commands.BadColourArgument):
            await interaction.response.send_message(
                embed=await ErrEmbed(self, text = f"A fost introdus un cod de culoare incorect."), ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            await interaction.response.send_message(
               embed=await ErrEmbed(self, text = f"Membru necunoscut pe server."), ephemeral=True)
        elif isinstance(error, disnake.errors.InteractionTimedOut):
            await interaction.response.send_message(
               embed=await ErrEmbed(self, text = f"A apărut o eroare la executarea comenzii.\nÎncercați din nou."), ephemeral=True)
        else:
            await interaction.response.send_message(
               embed=await ErrEmbed(self, text = f"A apărut o eroare la executarea comenzii.\n{error}"), ephemeral=True)

def setup(bot: CustomClient):
  bot.add_cog(Main(bot))
