import disnake

async def ErrEmbed(self, text: str) -> disnake.Embed:
    embed = disnake.Embed(title='⚠️ | Eruare', description=f'**{text}**', colour = disnake.Colour.red())
    embed.set_footer(text=self.bot.user.display_name + ' | Eruare', icon_url=self.bot.user.display_avatar.url)

    return embed