import disnake
from disnake.ext import commands
from Tools.Database import DataBase

class CustomClient(commands.Bot):
    db: DataBase

    def __init__(self):        
        super().__init__(intents=disnake.Intents.all(), command_prefix="dgdfgdfgdfgdgf", test_guilds=[1198496458329038909])
        self.db = DataBase()