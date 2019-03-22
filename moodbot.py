#!/usr/bin/python3

import json
import asyncio
import websockets
import datetime
import csv

class Message():
    def __init__(self, time, user, message):
        self.time = time
        self.user = user
        self.message = message

class MoodBot():
    def __init__(self, channel, oauth, average_seconds):
        self.channel = channel
        self.oauth = oauth
        self.average_seconds = average_seconds
        self.messages = []
        self.average = 0

    async def calculate_average(self):
        while True:
            await asyncio.sleep(max(self.average_seconds / 100, 5))
            now = datetime.datetime.now()
            self.messages = [m for m in self.messages if (m.time - now).seconds > self.average_seconds]
            self.average = len(self.messages) / self.average_seconds
            print(f"Average per second is {self.average}")

    async def run(self):
        self.websocket = await websockets.connect('wss://irc-ws.chat.twitch.tv:443')
        await self.connect_and_join()
        while True:
            line = await self.websocket.recv()
            print(line)
            if line[:4] == "PING":
                await self.handle_ping()
            else:
                self.handle_message(line)

    async def connect_and_join(self):
        await self.websocket.send(f"PASS {self.oauth}")
        await self.websocket.send("NICK moodbottv")
        greeting = await self.websocket.recv()
        await self.websocket.send(f"JOIN #{self.channel}")
        join_line = await self.websocket.recv()
        names_line = await self.websocket.recv()

    async def handle_ping(self):
        print("Ping recieved")
        await self.websocket.send("PONG :tmi.twitch.tv")
        print("Pong sent")

    def handle_message(self, line):
        user, message_text = self.parse_message(line)
        message = Message(datetime.datetime.now(), user, message_text)
        self.messages.append(message)

    def parse_message(self, line):
        parts = line.split(":")
        user = parts[1].split("!")[0]
        message = parts[-1].replace("\n", "")
        return user, message

def main():
    cfg = json.loads(open("bot.cfg", "rb").read())
    oauth = cfg["OAuth"]
    moodbot = MoodBot("danielfenner", oauth, 600)
    loop = asyncio.get_event_loop()
    loop.create_task(moodbot.calculate_average())
    loop.run_until_complete(moodbot.run())

if __name__ == '__main__':
    main()
