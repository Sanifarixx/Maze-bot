

async def getshoproles(interguildid) -> list:

    result = getConfig(interguildid)

    if result:
        pingRoles = result['pingroles']
    else:
        pingRoles = []
    return pingRoles

async def getFamShopRoles(interguildid) -> list:

    result = getConfig(interguildid)

    if result:
        pingRoles = result['famPingRoles']
    else:
        pingRoles = []
    return pingRoles