from datetime import datetime
from config import TOKEN
from Classes.CustomClient import CustomClient
from Tools.etcTools import load_cogs

bot = CustomClient()

@bot.event
async def on_ready():
    await load_cogs(bot)
    print(f'{datetime.now()} - START')

bot.run(TOKEN)