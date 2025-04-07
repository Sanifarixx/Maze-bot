import disnake

async def getFamLogChannel(self, interguildid: int) -> disnake.TextChannel:

    result = await self.bot.db.get_config(interguildid)

    if result:
        channel = self.bot.get_channel(result['famlog'])
    else: channel = None

    return channel

async def getEconomyLogChannel(self, interguildid: int) -> disnake.TextChannel:
    
    result = await self.bot.db.get_config(interguildid)

    if result:
        channel = self.bot.get_channel(result['economylog'])
    else: channel = None

    return channel

async def getModerationLogChannel(self, interguildid: int) -> disnake.TextChannel:

    result = await self.bot.db.get_config(interguildid)

    if result:
        channel = self.bot.get_channel(result['moderationLog'])
    else: 
        channel = None

    return channel

async def privateRoomsLog(self, interguildid: int) -> disnake.TextChannel:
    result = await self.bot.db.get_config(interguildid)

    if result:
        channel = self.bot.get_channel(result['privateRoomLog'])
    else: channel = None

    return channel

async def getTicketLogChannel(self, interguildid: int) -> disnake.TextChannel:
    result = await self.bot.db.get_config(interguildid)

    if result:
        channel = self.bot.get_channel(result['ticketLog'])
    else: channel = None

    return channel