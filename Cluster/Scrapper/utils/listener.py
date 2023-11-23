from telethon import TelegramClient
import telethon
from telethon.tl.functions.messages import ImportChatInviteRequest
import loguru
from asyncio import sleep
from asyncstdlib import enumerate as async_enumerate
import json
import datetime
import os
from database_binding import DataBaseBinding
import yaml


class TelegramChatListener:
    def __init__(self):
        self.api_id = self.__load_config('telethon')['api_id']
        self.api_hash = self.__load_config('telethon')['api_hash']
        self.database = DataBaseBinding(self.__load_config('telethon')['database'])
        self.chat_url = self.__load_config('telethon')['chat_url']
        self.max_messages = self.__load_config('telethon')['max_messages']
        self.timeout = self.__load_config('telethon')['timeout']

        self.database.create_tables()
        self.client = TelegramClient("listener", api_id=self.api_id, api_hash=self.api_hash)

        with open('../../../configs/is_authorized.json', 'r') as is_athorized:
            raw_auth = json.load(is_athorized)
            if not raw_auth:
                self.joined_chat = {"authorized_groups":[]}
            else:
                self.joined_chat = raw_auth

        with open('../../../configs/last_timestamp.json', 'r') as timestamp:
            raw_stamp = json.load(timestamp)
            if not raw_stamp:
                self.last_timestamp = {}
            else:
                self.last_timestamp = raw_stamp
    
    def __load_config(self, setting):
        with open('../../../configs/main.yaml', 'r') as config:
            config = yaml.safe_load(config)
            return config[setting]

    def __verify_link(self, chat_link: str):
        if chat_link.startswith("https://t.me/"):
            return True
        else:
            return False
    

    async def __join_chat(self, chat_link: str):
        if self.__verify_link(chat_link):
            try:
                await self.client(ImportChatInviteRequest(hash=chat_link[14:]))
            except telethon.errors.rpcerrorlist.UserAlreadyParticipantError:
                loguru.logger.info("User is already a participant of this chat.")
        else:
            loguru.logger.error("The chat link provided is not a valid Telegram chat link.")
    

    async def listen(self):

        if not self.chat_url in self.joined_chat["authorized_groups"]:
            await self.__join_chat(self.chat_url)
            self.joined_chat["authorized_groups"].append(self.chat_url)
            with open('../../../configs/is_authorized.json', 'w') as is_athorized:
                            json.dump(self.joined_chat, is_athorized)

        entity = await self.client.get_entity(self.chat_url)
        try:
            async with self.client:
                async for i, message in async_enumerate(self.client.iter_messages(entity)):
                    if i > self.max_messages:
                        self.max_messages+= self.max_messages
                        await sleep(self.timeout)

                    date = message.date
                    if self.last_timestamp:
                        if date <= datetime.datetime.fromisoformat(self.last_timestamp[self.chat_url]):
                            break
                    if i == 0:
                        with open('../../../configs/last_timestamp.json', 'w') as timestamp:
                            timestamp_copy = self.last_timestamp.copy()
                            timestamp_copy[self.chat_url] = date.isoformat()
                            json.dump(timestamp_copy, timestamp)

                    id = message.id
                    text = message.text
                    reactions = message.reactions.results[0].reaction.emoticon \
                                if message.reactions else None
                
                    if message.from_id:
                        user_id = message.from_id.user_id
                        username_future = await self.client.get_entity(user_id)
                        username = username_future.username

                    else:
                        user_id = None
                        username = None

                    reply_to_msg_id = message.reply_to.reply_to_msg_id \
                                      if message.reply_to else None
            
            self.database.insert_data(
                {
                    'message_id': id,
                    'time_uploaded': date,
                    'user_id': user_id,
                    'username': username,
                    'reply_to_msg_id': reply_to_msg_id,
                    'text': text,
                    'reactions': reactions
                }
            )
                
        except Exception as e:
            loguru.logger.error(f"Failed to parse message: {e}")

if __name__ == "__main__":
    
    listener = TelegramChatListener()
    with listener.client:
        listener.client.loop.run_until_complete(
            listener.listen(chat_url='https://t.me/endeavourosru')
            )
                