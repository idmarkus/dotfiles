import json
from pathlib import Path

from cuthelpers import *


class Rooms():
    ROOMTRIM_FRAMECOUNT = 27
    EventNames = dict()
    EventNames[0] = "USE_CARD"
    EventNames[1] = "USE_PILL"
    EventNames[3] = "TAKE_DAMAGE"
    EventNames[4] = "PICKUP_ITEM"
    EventNames[5] = "PICKUP_HEART"
    EventNames[6] = "PICKUP_CONSUMABLE"
    EventNames[7] = "PICKUP_TRINKET"
    EventNames[8] = "OPEN_CHEST"
    EventNames[9] = "ROOM_CLEARED"

    def __init__(self, _rooms, start_time, duration=None):
        self._rooms = _rooms
        self.add_names()
        self.fix_eventnames()
        duration = duration or 0
        self.fix_times(start_time, duration)

        self.calc_dps()
        self.ensure_rewinds()
        self.add_collectibles()

    def __iter__(self):
        return self._rooms.__iter__()

    def __next__(self):
        return self._rooms.__next__()

    def __len__(self):
        return self._rooms.__len__()

    def __getitem__(self, index):
        if isinstance(index, tuple):
            raise Exception("Whatever.. rooms cannot have multiple indices[]")
        elif isinstance(index, str):
            return self.get_name(index)
        else:
            return self._rooms[index]

    def get_name(self, name):
        for r in self._rooms:
            if r["name"] == name:
                return r

    def fix_eventnames(self):
        for r in self:
            for e in r["events"]:
                e["id"] = self.EventNames[e["id"]]

    def fix_times(self, start_time, duration=None):
        # Change times to sec and trim
        for i, room in enumerate(self):
            t = room["time"]

            if i == 0:
                t[0] = 0
            else:
                t[0] = ms_to_sec(t[0] - start_time) - frame_to_sec(self.ROOMTRIM_FRAMECOUNT)

            if i < (len(self._rooms) - 1):
                t[1] = ms_to_sec(t[1] - start_time) - (frame_to_sec(self.ROOMTRIM_FRAMECOUNT) * 2)
            else:  # if on the last room
                t[1] = duration

            # events = room["events"]
            for e in room["events"]:
                e["time"] = ms_to_sec(e["time"] - start_time)

            if "pauses" in room.keys():
                for p in room["pauses"]:
                    p[0] = ms_to_sec(p[0] - start_time)
                    p[1] = ms_to_sec(p[1] - start_time)

    def add_names(self):
        for i, v in enumerate(self):
            v["name"] = "{}:{}".format(v["stage"], v["roomIndex"])
            v["_ord"] = i

    def add_collectibles(self):
        collectibles = []
        seen = set()
        for v in self:
            for e in v["events"]:
                if e["id"] == "PICKUP_ITEM":
                    if e["item"] in seen: continue
                    collectibles.append({
                        "item": e["item"],
                        "quality": e["quality"],
                        "stage": v["stage"]
                    })
                    seen.add(e["item"])
        self.collectibles = collectibles

    def ensure_rewinds(self):
        from collections import Counter

        cnt = Counter([x['name'] for x in self._rooms if x["isFirstVisit"]])
        for name, count in cnt.most_common():
            if name == '11:163':
                print("count: {}".format(count), flush)
            if count <= 1: break
            rem = count - 1
            for i, r in enumerate(self):
                if r["name"] == name:
                    r["isRewind"] = True
                    r["name"] += ":rem"
                    if (i + 1) < len(self):
                        self[i + 1]["isRewind"] = True
                    rem -= 1
                    if rem <= 0: break

        for i, r in enumerate(self):
            if r["frame"][1] == 0: continue

            if r["frame"][1] - r["frame"][0] < 4:
                r["isRewind"] = True
                if (i + 1) < len(self):
                    self[i + 1]["isRewind"] = True

    def calc_dps(self):
        stages = {}

        # for i, r in enumerate(_rooms):
        for i, r in enumerate(self):
            c0 = (not "dmg" in r.keys()) \
                 or (r["dmg"] == 0) \
                 or (not r["isHostile"])
            # or (r["roomType"] != "ROOM_DEFAULT")

            if c0: continue

            cleared = 0
            for e in r["events"]:
                if e["id"] == 9 or e["id"] == "ROOM_CLEARED":
                    cleared = e["time"]
                    break
            else:
                continue

            stage = r["stage"]
            if not stage in stages.keys():
                stages[stage] = []

            time = cleared - r["time"][0]
            dmg = r["dmg"]
            r["dps"] = dmg / time
            stages[stage].append({"idx": r["roomIndex"], "dps": r["dps"]})
            # if r["roomType"] == "ROOM_BOSS":
            # print("{}: {}".format(r["name"], r["dps"]), flush=True)

        avgs = {}
        for k, v in stages.items():
            total = sum(map(lambda x: x["dps"], v))
            avgs[k] = total / len(v)

        for k, v in stages.items():
            stages[k] = sorted(v, key=lambda x: x["dps"], reverse=True)

        self.stage_dps_avg = avgs
        self.stage_dps_list = stages
