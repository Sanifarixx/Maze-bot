import disnake

async def getEconomyAccess(self, interauthor: disnake.Member) -> bool:
    
    result = await self.bot.db.get_config(interauthor.guild.id)

    roles = result['economyPermRoles']

    for role in interauthor.roles:
        if role.id in roles:
            return True
    return False

async def getFamAccess(self, interauthor: disnake.Member) -> bool:
   
    result = await self.bot.db.get_config(interauthor.guild.id)

    roles = result['famPermRoles']

    for role in interauthor.roles:
        if role.id in roles:
            return True
    return False

async def getModerAccess(self, interauthor: disnake.Member) -> bool:
   
    result = await self.bot.db.get_config(interauthor.guild.id)

    roles = result['moderPermRoles']

    for role in interauthor.roles:
        if role.id in roles:
            return True
    return False

async def getBanAccess(self, interauthor: disnake.Member) -> bool:
   
    result = await self.bot.db.get_config(interauthor.guild.id)

    roles = result['banPermRoles']

    for role in interauthor.roles:
        if role.id in roles:
            return True
    return False