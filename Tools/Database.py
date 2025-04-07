from typing import Optional
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from config import DB_CONNECTION_STRING

class DataBase:
     def __init__(self):
          self.__client = AsyncIOMotorClient(DB_CONNECTION_STRING)
          self.__db = self.__client['sample_mflix']
          self.__configCollection = self.__db['config']
          self.__contextCollection = self.__db['context']
          self.__moderationCollection = self.__db['moderation']
          self.__messagesColection = self.__db['messages']
          
     async def delete_message(self, filter: dict):
          await self.__messagesColection.delete_one(filter)

     async def insert_message(self, data):
          await self.__messagesColection.insert_one(data)

     async def get_messages(self, guildId: int, memberId: int):
          return self.__messagesColection.find({'guildId': guildId, 'memberId': memberId})

     async def get_config(self, guildId: int) -> Optional[dict]:
          return await self.__configCollection.find_one({'guildId': guildId})

     async def update_config(self, guildId:int, data: dict):
          await self.__configCollection.update_one({'guildId': guildId}, {'$set': data})

     async def insert_config(self, data):
          await self.__configCollection.insert_one(data)

     async def get_context(self, filter: dict, many: bool = False) -> Optional[dict]:
          if many:
               self.__contextCollection.find(filter)
          else:
               return await self.__contextCollection.find_one(filter)

     async def insert_context(self, data: dict):
          await self.__contextCollection.insert_one(data)

     async def update_context(self, filter: dict, data: dict, many: bool = False):
          if many:
               await self.__contextCollection.update_many(filter, {'$set': data})
          else:
               await self.__contextCollection.update_one(filter, {'$set': data})


     async def delete_context(self, filter: dict, many: bool = False):
          if many:
               await self.__contextCollection.delete_many(filter)
          else:
               await self.__contextCollection.delete_one(filter)

     async def insert_punish(self, data: dict):
          await self.__moderationCollection.insert_one(data)

     async def delete_punish(self, filter: dict, many: bool = False):
          if many:
               await self.__moderationCollection.delete_many(filter)
          else:
               await self.__moderationCollection.delete_one(filter)

     async def get_punish(self, filter: dict, many: bool = False) -> dict:
          if many:
               response = self.__moderationCollection.find(filter)
          else:
               response = await self.__moderationCollection.find_one(filter)

          return response

     async def update_punish(self, filter: dict, data: dict, many: bool = False):
          if many:
               await self.__moderationCollection.update_many(filter, {'$set': data})
          else:
               await self.__moderationCollection.update_one(filter, {'$set': data})