#!/usr/bin/python3

import json
import asyncio
import websockets
import datetime
import csv

class MoodBot():
    def __init__(self, channel, oauth):
        self.channel = channel
        self.oauth = oauth

    async def run(self):
        #self.websocket = await websockets.connect('wss://irc-ws.chat.twitch.tv:443')
        async with websockets.connect('wss://irc-ws.chat.twitch.tv:443') as websocket:
            await websocket.send(f"PASS {self.oauth}")
            await websocket.send("NICK moodbottv")
            greeting = await websocket.recv()
            await websocket.send(f"JOIN #{self.channel}")
            join_line = await websocket.recv()
            names_line = await websocket.recv()
            while True:
                line = await websocket.recv()
                print(line)
                if line[:4] == "PING":
                    await self.handle_ping(websocket)
                else:
                    self.handle_message(line)
        
    def parse_message(self, line):
        parts = line.split(":")
        user = parts[1].split("!")[0]
        message = parts[-1].replace("\n", "")
        return user, message

    async def handle_ping(self, websocket):
        print("Ping recieved")
        await websocket.send("PONG :tmi.twitch.tv")
        print("Pong sent")

    def handle_message(self, line):
        f = open("messages.csv", "ab")
        user, message = self.parse_message(line)
        f.write(bytes(str(datetime.datetime.now()) + "," + user + "," + message + "\n", "utf8"))
        f.close()

async def main():
    cfg = json.loads(open("bot.cfg", "rb").read())
    oauth = cfg["OAuth"]
    moodbot = MoodBot("danielfenner", oauth)
    await moodbot.run()

if __name__ == '__main__':
    #main()
    asyncio.get_event_loop().run_until_complete(main())
