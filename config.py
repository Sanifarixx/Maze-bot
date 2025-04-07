TOKEN = ''

DELETE_ERROR_SECONDS = 10

USER_AUTH_TOKEN = ''

DB_CONNECTION_STRING = ''
TYPES_WITH_DURATION = ['BAN', 'MUTE', 'VMUTE', 'MPMUTE', 'BANROLEREQUEST', 'TICKETBAN']

DM_DATA = {
        'KICK': 'Ați fost eliminat de pe server',
        'BAN': 'Ați fost blocat pe server',
        'MUTE': 'Vi s-a emis o blocare pe server',
        'VMUTE': 'Vi s-a aplicat o interdicție vocală pe server',
        'MPMUTE': 'Vi s-a aplicat o blocare a platformei de tranzacționare pe server',
        'BANROLEREQUEST': 'Vi s-a aplicat o blocare pentru cererea de roluri pe server',
        'TICKETBAN': 'Accesul la tichete pe server v-a fost blocat',
    }

RESPONSE_DATA = {
        'KICK': ['Eliminare utilizator', 'a fost eliminat de către un moderator'],
        'BAN': ['Blocare utilizator', 'a fost blocat de către un moderator'],
        'UNBAN': ['Deblocare utilizator', 'a fost deblocat de către un moderator'],
        'MUTE': ['Blocare pe chat', 'blocarea pe chat a fost aplicată de un moderator'],
        'UNMUTE': ['Deblocare pe chat', 'blocarea pe chat a fost ridicată de un moderator'],
        'VMUTE': ['Blocare pe canale vocale', 'blocarea pe voce a fost aplicată de un moderator'],
        "UNVMUTE": ['Deblocare pe canale vocale', 'blocarea pe voce a fost ridicată de un moderator'],
        'MPMUTE': ['Blocare pe platforma de tranzacționare', 'blocarea pe platforma de tranzacționare a fost aplicată de un moderator'],
        'UNMPMUTE': ['Deblocare pe platforma de tranzacționare', 'blocarea pe platforma de tranzacționare a fost ridicată de un moderator'],
        'BANROLEREQUEST': ['Blocare pentru cererea de roluri', 'blocarea pentru cererea de roluri a fost aplicată de un moderator'],
        'TICKETBAN': ['Blocare pe tichete', 'blocarea pe tichete a fost aplicată de un moderator'],
        'UNTICKETBAN': ['Deblocare pe tichete', 'blocarea pe tichete a fost ridicată de un moderator'],
    }
