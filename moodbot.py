#!/usr/bin/python3

import json
import asyncio
import websockets

def parse_message(line):
    parts = line.split(":")
    user = parts[1].split("!")[0]
    message = parts[-1]
    return user, message

async def main():
    cfg = json.loads(open("bot.cfg", "rb").read())
    oauth = cfg["OAuth"]
    async with websockets.connect('wss://irc-ws.chat.twitch.tv:443') as websocket:
        await websocket.send("PASS " + oauth)
        await websocket.send("NICK moodbottv")
        greeting = await websocket.recv()
        print(f"{greeting}")
        await websocket.send("JOIN #danielfenner")
        while True:
            line = await websocket.recv()
            user, message = parse_message(line)
            print(f"{user}: {message}")


asyncio.get_event_loop().run_until_complete(main())
