import time
import sys

import logging

logging.basicConfig(level=logging.INFO)

from obswebsocket import obsws, requests
from ffmpegtest import ffprobe_duration

import socket

from pathlib import Path
from win32api import GetTickCount


class OBSio:
    AUTH = ("localhost", 4444, "")
    filename = ""

    def __init__(self):
        self.client = obsws(*self.AUTH)

    # def printVers(self):
    #     self.client.connect()
    #     vers = self.client.call(requests.GetVersion())
    #     print(vers, flush=True)
    #     self.client.disconnect()

    async def startRecord(self):
        try:
            self.client.connect()
            self.client.call(requests.StartRecording())
            self.start_time = GetTickCount()
            status = self.client.call(requests.GetRecordingStatus())
            self.filename = status.getRecordingFilename()
            self.client.disconnect()
            return self.start_time
        except Exception as e:
            print(str(e), flush=True)
            return 0

    def stopRecord(self):
        try:
            self.client.connect()
            status = self.client.call(requests.GetRecordingStatus())
            if not status.getIsRecording:
                raise Exception("Not recording.")
            self.filename = status.getRecordingFilename()
            self.client.call(requests.StopRecording())
            self.client.disconnect()
        except Exception as e:
            print(str(e), flush=True)


import socket
import json
import asyncio

obs = OBSio()


async def handle_data(reader, writer):
    data = await reader.read()
    struct = json.loads(data)
    if (struct['request'] == 'start'):
        ret = obs.startRecord()
        await ret
        # print(struct, flush=True)
        print("Run has began: {} | obs_start: {}".format(struct["seed"], obs.start_time), flush=True)
        writer.write(str(ret).encode('utf8'))
        await writer.drain()
        writer.close()
    elif (struct['request'] == 'end'):
        print("Run has ended: {} | game_start: {}".format(struct["seed"], struct["start_time"]), flush=True)
        obs.stopRecord()

        struct["vid_filename"] = obs.filename
        struct["obs_starttime"] = obs.start_time

        print("Finished recording: {}".format(obs.filename), flush=True)

        duration = ffprobe_duration(obs.filename)

        if len(struct["rooms"]) < 10:
            print("Removing short run {} {} {}".format(struct["seed"], struct["char"], obs.filename), flush=True)
            rem_p = Path(obs.filename)
            rem_p.unlink()
        else:
            # Just keep it if ffprobe failed
            out_d = Path("./uncut")
            out_d.mkdir(exist_ok=True)
            out_p = out_d / "{}{}.json".format(struct["seed"], struct["char"])
            with open(str(out_p), "w") as f:
                json.dump(struct, f)
        # for i, room in enumerate(struct["trace"]):
        #     print("  {}".format(i), flush=True)
        #     for k, v in room.items():
        #         print("    {}:  {}".format(k, v), flush=True)


async def main():
    server = await asyncio.start_server(handle_data, '127.0.0.1', 12001)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}', flush=True)

    async with server:
        await server.serve_forever()


asyncio.run(main())
