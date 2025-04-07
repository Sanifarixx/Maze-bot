import disnake
from datetime import datetime
from Tools.Get.Different import time_diff

class Punish:
    def __init__(self, inter: disnake.ApplicationCommandInteraction, type: str, member: disnake.Member, reason: str, duration: str = None, endTime : int = None):
        self.member = member
        self.reason = reason
        self.inter = inter
        self.duration = duration
        self.endTime = endTime
        self.type = type

    async def to_dict(self) -> dict:
        data = {
            'type': self.type,
            'guildId': self.inter.guild.id,
            'moderId': self.inter.author.id,
            'memberId': self.member.id,
            'reason': self.reason,
            'duration': self.duration,
            'endTime': self.endTime,
            'timeNow': await time_diff(),
            'date': datetime.now().strftime("%d.%m.%Y")
        }

        return data