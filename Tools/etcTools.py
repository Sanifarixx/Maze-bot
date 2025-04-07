from Classes.CustomClient import CustomClient

async def load_cogs(bot: CustomClient) -> None:
    bot.load_extension('Cogs.main')
    bot.load_extension("Cogs.moderation")
    bot.load_extension("Cogs.embed")
    bot.load_extension("Cogs.parsers")