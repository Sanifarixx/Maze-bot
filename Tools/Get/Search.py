import disnake


async def search_personal_role(inter: disnake.ApplicationCommandInteraction, text_input: str):
    context = await getContexts({'type': 'personalRole', 'guildId': inter.guild.id})
    response = []
    text_input_lower = text_input.lower()
    async for item in context:
        role = inter.guild.get_role(item['roleId'])
        if text_input_lower in role.name.lower():
            response.append(role.name)
    return response

async def search_fam(inter: disnake.ApplicationCommandInteraction, user_input: str) -> list:

        fams = await getFamList(inter.guild.id)

        result = []
        user_input_lower = user_input.lower()
        async for fam in fams:
            fam_role = disnake.utils.get(inter.guild.roles, id = fam["roleId"])
            if user_input_lower in fam_role.name.lower():
                result.append(fam_role.name)
        return result

async def searchFamProduct(inter: disnake.ApplicationCommandInteraction, user_input: str) -> list:
    result = await getConfig(inter.guild.id)

    return [f"{item[0]} цена: {item[1]}" for item in result["famProducts"]]