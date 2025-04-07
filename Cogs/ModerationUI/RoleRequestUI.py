import disnake
from datetime import datetime

from config import DELETE_ERROR_SECONDS
from Classes.CustomClient import CustomClient
from Tools.Get.Different import time_diff, get_time_difference
from Tools.Get.Check import check_nickname_format
from Tools.GeneralUI import ErrEmbed


class RoleRequestButtons(disnake.ui.View):
    def __init__(self, bot: CustomClient):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label="Aprobă cererea", style=disnake.ButtonStyle.green, custom_id="roleRequestAccept")
    async def button_1_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = inter.message.embeds[0]
        member = await inter.guild.fetch_member(int(embed.fields[0].value[2:-1]))
        if not member:
            member = await self.bot.fetch_user(int(embed.fields[0].value[2:-1]))
        nickname = embed.fields[1].value
        gettrole = inter.guild.get_role(int(embed.fields[2].value[3:-1]))
        await inter.message.reply(
            f'`[✔ | APROBAT] `{inter.author.mention}` a aprobat cererea pentru rolul de la `{member.mention}` cu nickname-ul {nickname}`{await get_time_difference(inter.message)}'
        )
        try:
            await member.add_roles(gettrole)
            await member.send(
                f'`[{inter.guild.name}][✔ | APROBAT] `{member.mention}` cererea ta pentru rolul [{gettrole.name}] a fost aprobată de moderatorul `{inter.author.mention}`{inter.author.display_name}`'
            )
        except:
            config = await self.bot.db.get_config(inter.guild.id)
            if config['botnotify']:
                channel = self.bot.get_channel(config['botnotify'])
                if channel:
                    await channel.send(
                        f'`[✔ | APROBAT] `{member.mention}` cererea ta pentru rolul [{gettrole.name}] a fost aprobată de moderatorul `{inter.author.mention}`{inter.author.display_name}`'
                    )
        await inter.message.delete()
        date = datetime.now().strftime("%d.%m.%Y")

        data = {
            'type': 'ROLE_ACCEPT',
            'guildId': inter.guild.id,
            'moderId': inter.author.id,
            'memberId': member.id,
            'reason': None,
            'duration': None,
            'timeNow': await time_diff(),
            'endTime': None,
            'date': date
        }

        await self.bot.db.insert_punish(data)
        await self.bot.db.delete_context({'messageId': inter.message.id})

    @disnake.ui.button(label="Respinge cererea", style=disnake.ButtonStyle.red, custom_id="roleRequestDecline")
    async def button_2_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = inter.message.embeds[0]
        member = await self.bot.fetch_user(int(embed.fields[0].value[2:-1]))
        nickname = embed.fields[1].value
        gettrole = inter.guild.get_role(int(embed.fields[2].value[3:-1]))
        await inter.message.reply(
            f'`[✖ | RESPINS] `{inter.author.mention}` a respins cererea pentru rolul de la `{member.mention}` cu nickname-ul {nickname}`\n{await get_time_difference(inter.message)}'
        )
        try:
            await member.send(
                f'`[{inter.guild.name}][✖ | RESPINS] `{member.mention}` cererea ta pentru rolul [{gettrole.name}] a fost respinsă de moderatorul `{inter.author.mention}`{inter.author.display_name}`'
            )
        except:
            config = await self.bot.db.get_config(inter.guild.id)
            if config['botnotify']:
                channel = self.bot.get_channel(config['botnotify'])
                if channel:
                    await channel.send(
                        f'`[✖ | RESPINS] `{member.mention}` cererea ta pentru rolul [{gettrole.name}] a fost respinsă de moderatorul `{inter.author.mention}`'
                    )
        await inter.message.delete()
        await self.bot.db.delete_context({'messageId': inter.message.id})

    @disnake.ui.button(label="Solicită statistici", style=disnake.ButtonStyle.blurple, custom_id="roleRequestGetStat")
    async def button_3_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        button.disabled = True
        await inter.response.edit_message(view=self)
        embed = inter.message.embeds[0]
        member = await self.bot.fetch_user(int(embed.fields[0].value[2:-1]))
        nickname = embed.fields[1].value
        await inter.message.reply(
            f'`[📬 | STATISTICI] `{inter.author.mention}` a solicitat statistici de la utilizatorul `{member.mention}` cu nickname-ul {nickname}`'
        )
        try:
            await member.send(
                f'`[{inter.guild.name}][📬 | STATISTICI] `{member.mention}`, moderatorul `{inter.author.mention}` ți-a solicitat statistici pentru contul tău de joc.`\n> Cum să trimiți corect statisticile?\n\n1. Fă o captură de ecran în joc cu statisticile tale `[/stats + /time].`\n2. Trimite statisticile tale botului care ți-a trimis acest mesaj.\n3. Dacă moderarea nu răspunde, încearcă să trimiți direct moderatorului care a solicitat statisticile.'
            )
            def check(message: disnake.Message):
                return message.author == member and message.attachments
            message = await self.bot.wait_for('message', check=check)
            embed = inter.message.embeds[0]
            attachment = message.attachments[0]
            embed.set_image(url=attachment.url)
            await inter.message.edit(embed=embed)
            await inter.message.reply(
                f'`[📬 | STATISTICI] `{inter.author.mention}, {member.mention}` a actualizat statisticile sale. Pentru a le vizualiza, accesează acest [mesaj](https://discord.com/channels/{inter.guild.id}/{inter.channel.id}/{inter.message.id})\n`[❔ | DEBUG]`||[IMAGE_URL]({attachment.url})||'
            )
        except:
            pass

    @disnake.ui.button(label="Șterge cererea", style=disnake.ButtonStyle.grey, custom_id="deleteRoleRequest")
    async def button_4_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = inter.message.embeds[0]
        member = await self.bot.fetch_user(int(embed.fields[0].value[2:-1]))
        nickname = embed.fields[1].value
        gettrole = inter.guild.get_role(int(embed.fields[2].value[3:-1]))
        await inter.message.reply(
            f'`[🛑 | ȘTERS] `{inter.author.mention}` a șters cererea pentru rolul de la `{member.mention}` cu nickname-ul {nickname}`'
        )
        await inter.message.delete()
        try:
            await member.send(
                f'`[{inter.guild.name}][🛑 | ȘTERS] `{member.mention}` cererea ta pentru rolul [{gettrole.name}] a fost ștearsă de moderatorul `{inter.author.mention}`{inter.author.display_name}`'
            )
        except:
            pass
        await self.bot.db.delete_context({'messageId': inter.message.id})


class RoleRequestDropDown(disnake.ui.StringSelect):
    def __init__(self, bot: CustomClient, guildId: int):
        self.bot = bot
        self.guildId = guildId
        options = []  # Inițializare opțiuni
        super().__init__(
            options=options,
            placeholder="Selectați organizația",
            min_values=1,
            max_values=1,
            custom_id='roleRequestDropDownId'
        )
    
    async def load_options(self):
        config = await self.bot.db.get_config(self.guildId)  # Aici folosești await pentru a obține configurația asincron
        options = []
        for orgRole in config.get('organizationalRoles', []):
            options.append(disnake.SelectOption(label=orgRole[0], value=orgRole[1]))
        self.options = options  # Actualizezi opțiunile cu cele corecte



class RoleRequestModal(disnake.ui.Modal):
    def __init__(self, bot: CustomClient, data: dict):
        self.bot = bot
        self.data = data
        components = [
            disnake.ui.TextInput(
                label="Nickname (Formatul Nick_Name)",
                custom_id="value1",
                style=disnake.TextInputStyle.short,
                max_length=35,
            ),
            disnake.ui.TextInput(
                label="Rang",
                custom_id="value2",
                style=disnake.TextInputStyle.short,
                max_length=2
            ),
        ]
        custom_id = 'roleRequestModal'
        title = "Cerere pentru rol"

        super().__init__(
            title=title,
            components=components,
            custom_id=custom_id
        )

    async def callback(self, inter: disnake.ModalInteraction):
        nickname = inter.text_values["value1"]
        if await check_nickname_format(nickname):
            if inter.text_values["value2"] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                config = await self.bot.db.get_config(inter.guild.id)
                if config['getrolechannel']:
                    channel = self.bot.get_channel(config['getrolechannel'])
                else:
                    channel = None

                if channel:
                    embed = disnake.Embed(
                        title='[✅] Realizat cu succes!',
                        description='**Cererea ta pentru rol a fost trimisă. Așteaptă procesarea acesteia.**',
                        colour=disnake.Colour.green()
                    )
                    embed.set_footer(text=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
                    await inter.response.send_message(
                        embed=embed,
                        ephemeral=True
                    )

                    role = next((r[1] for r in config['organizationalRoles'] if r[0] == self.data["role"]), None)
                    if role:
                        role = inter.guild.get_role(int(role))

                    if role:
                        request_embed = disnake.Embed(
                            title="Cerere pentru rol",
                            description=f"{inter.author.mention} a trimis o cerere pentru rolul: {role.mention}.",
                            colour=disnake.Colour.blue(),
                            timestamp=datetime.now()
                        )
                        request_embed.add_field(name="Utilizator", value=f"{inter.author.mention}")
                        request_embed.add_field(name="Nickname", value=f"`{nickname}`")
                        request_embed.add_field(name="Rang", value=f"`{inter.text_values['value2']}`")
                        request_embed.add_field(name="Rol solicitat", value=f"{role.mention}")
                        request_embed.set_footer(text=f"ID: {inter.author.id}", icon_url=inter.author.display_avatar.url)

                        await channel.send(embed=request_embed, view=RoleRequestButtons(self.bot))
                        await self.bot.db.insert_context(
                            {"messageId": channel.last_message_id, "guildId": inter.guild.id}
                        )
                    else:
                        error_embed = disnake.Embed(
                            title="Eroare",
                            description="Rolul solicitat nu a fost găsit.",
                            colour=disnake.Colour.red()
                        )
                        await inter.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    error_embed = disnake.Embed(
                        title="Eroare",
                        description="Canalul de cereri pentru roluri nu a fost configurat.",
                        colour=disnake.Colour.red()
                    )
                    await inter.response.send_message(embed=error_embed, ephemeral=True)
            else:
                error_embed = disnake.Embed(
                    title="Eroare",
                    description="Rangul trebuie să fie între 1 și 10.",
                    colour=disnake.Colour.red()
                )
                await inter.response.send_message(embed=error_embed, ephemeral=True)
        else:
            error_embed = disnake.Embed(
                title="Eroare",
                description="Nickname-ul trebuie să respecte formatul `Nick_Name`.",
                colour=disnake.Colour.red()
            )
            await inter.response.send_message(embed=error_embed, ephemeral=True)
