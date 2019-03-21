#!/usr/bin/python3

import json
import asyncio
import pydle

# Simple echo bot.
class MyOwnBot(pydle.Client):
    async def on_connect(self):
        print("Connected!")
        await super().on_connect()
        await self.join("#danielfenner")

    # Override from base class
    async def on_message(self, timestamp, tags, channel, user, message):
        print(message)


client = MyOwnBot('moodbottv')
client.run('irc.chat.twitch.tv')

cfg = json.loads(open("bot.cfg", "rb").read())
oauth = cfg["OAuth"]
