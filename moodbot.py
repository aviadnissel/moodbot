#!/usr/bin/python3

import sys
import json
import asyncio
import websockets
import datetime
import csv
from termcolor import colored

COLORS = {0: 'red',
          1: 'red',
          2: 'red',
          3: 'yellow',
          4: 'yellow',
          5: 'yellow',
          6: 'yellow',
          7: 'yellow',
          8: 'green',
          9: 'green',
          10: 'green'}

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
        self.long_average = 0
        self.short_average = 0
        self.current_volume = 0
        self.start_time = datetime.datetime.now()

    async def print_volume(self):
        while True:
            await asyncio.sleep(1)
            target_volume = int(self.short_average)
            if self.long_average != 0:
                target_volume = 5 + 10 * ((self.short_average - self.long_average) / self.long_average)
                target_volume = min(int(round(target_volume)), 10)
            if target_volume > self.current_volume:
                self.current_volume = min(target_volume, self.current_volume + 3, 10)
            elif target_volume < self.current_volume:
                self.current_volume = max(target_volume, self.current_volume - 1, 0)
            volume_text = ("=" * self.current_volume).ljust(10)
            print("[" + colored(volume_text, COLORS[self.current_volume]) + "]")

    async def calculate_average(self):
        while True:
            await asyncio.sleep(1)
            now = datetime.datetime.now()
            long_seconds = min(self.average_seconds, (now - self.start_time).seconds)
            self.messages = [m for m in self.messages if (now - m.time).seconds < long_seconds]
            self.long_average = len(self.messages) / long_seconds

            short_seconds = min(self.average_seconds / 20, (now - self.start_time).seconds)
            short_seconds = max(short_seconds, 1)
            short_messages = [m for m in self.messages if (now - m.time).seconds < short_seconds]
            self.short_average = len(short_messages) / short_seconds
            diff = self.short_average - self.long_average
            #print(f"Long average {round(self.long_average, 2)}, Short average {round(self.short_average, 2)}, Diff {round(diff, 2)}")

    async def read_messages(self):
        self.websocket = await websockets.connect('wss://irc-ws.chat.twitch.tv:443')
        await self.connect_and_join()
        while True:
            line = await self.websocket.recv()
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
        await self.websocket.send("PONG :tmi.twitch.tv")

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
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <channel_name> [timeframe]")
        exit(1)
    channel = sys.argv[1]
    timeframe = 120
    if len(sys.argv) > 2:
        timeframe = int(sys.argv[2])
    moodbot = MoodBot(channel, oauth, timeframe)
    loop = asyncio.get_event_loop()
    loop.create_task(moodbot.calculate_average())
    loop.create_task(moodbot.print_volume())
    loop.run_until_complete(moodbot.read_messages())

if __name__ == '__main__':
    main()
