import json
import os
from pathlib import Path
from pprint import pprint

import datetime

from cuthelpers import *  # ms_to_frame, frame_to_sec, frame_to_ms, ms_to_sec
from rooms import Rooms

from ffmpegtest import subclip, conc_cut, mkcuts, xfade_conc, ffprobe_duration

from time import time

from opencvcut import cvcut

# run_name = "RL0L 2S2DAzazel"
# run_name = "0VDF 63V6Isaac"
# run_name = "L6YK N6S0Isaac"
run_name = "9MR6 SKX9Eden"

# ROOMTRIM_FRAMECOUNT = 10 # to make room cuts at the actual door transition
ROOMTRIM_FRAMECOUNT = 27  # to make room cuts at the actual door transition
FADE_DURATION = 0.5
CLEARED_END_PADDING = 2.2
# how long we are willing to wait between clear and room endtime
# to keep an unfaded door transition, when next selected room is the
# following room
DOORTRANSITION_WAIT_LIMIT = 4.0
DOORTRANSITION_WAIT_COMPROMISE = 3.0
ROOM_START_OFFSET = 0.8
BOSS_START_OFFSET = 0.5
EVENT_CUT_OFFSET = 1.0
BOSS_ROOM_TIMELIMIT = 60.0 * 2  # hush/boss rush longer than 4 minutes we cut down
BOSS_ROOM_TIMELIMIT_OFFSET = 45
BOSS_EVENT_CUT_OFFSET = 4.0


# for i, r in enumerate(rooms):
#     if i > 10: break
#     t = r["time"]
#     t[0] = str(datetime.timedelta(milliseconds=t[0]))
#     t[1] = str(datetime.timedelta(milliseconds=t[1]))
#     r["time"] = t
#     pprint(r)

# exit()

def fixTimes(_rooms, start_time, duration):
    # Change times to sec and trim

    for i, room in enumerate(_rooms):
        # Grab frame timestamps for manual testing
        # tstamp = room["time"].copy()
        # tstamp[0] = str(datetime.timedelta(milliseconds=tstamp[0]))
        # tstamp[1] = str(datetime.timedelta(milliseconds=tstamp[1]))
        # _rooms[i]["timestamp"] = tstamp

        t = room["time"]
        if i == 0:
            t[0] = 0
        else:
            t[0] = ms_to_sec(t[0] - start_time) - frame_to_sec(ROOMTRIM_FRAMECOUNT)

        if i < (len(_rooms) - 1):
            # if room["stage"] == _rooms[i+1]["stage"]:
            #     # for door transitions, use next room's start
            #     t[1] = ms_to_sec(_rooms[i+1]["time"][0]) - frame_to_sec(ROOMTRIM_FRAMECOUNT)
            # else:
            #     # for stage transitions, this is the most accurate
            #     t[1] = ms_to_sec(t[1]) + frame_to_sec(ROOMTRIM_FRAMECOUNT)
            t[1] = ms_to_sec(t[1] - start_time) - (frame_to_sec(ROOMTRIM_FRAMECOUNT) * 2)
        else:
            # if on the last room
            t[1] = duration

        # Append duration for manual testing
        t.append(t[1] - t[0])
        _rooms[i]["time"] = t

        # frames = [
        #     sec_to_frame(t[0]),
        #     sec_to_frame(t[1]),
        #     sec_to_frame(t[2])
        # ]
        # _rooms[i]["frames"] = frames

        events = room["events"]
        for e in events:
            e["time"] = ms_to_sec(e["time"] - start_time)
        _rooms[i]["events"] = events

        if "pauses" in room:
            pauses = room["pauses"]
            for p in pauses:
                p[0] = ms_to_sec(p[0] - start_time)
                p[1] = ms_to_sec(p[1] - start_time)
            _rooms[i]["pauses"] = pauses
    return _rooms


def calc_dpsavg(_rooms):
    stages = {}

    for i, r in enumerate(_rooms):
        cond_skip = (not "dmg" in r) \
                    or (r["dmg"] == 0) \
                    or (not r["isHostile"]) \
                    or (r["roomType"] != "ROOM_DEFAULT")

        if cond_skip: continue

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
        dps = dmg / time
        stages[stage].append({"idx": r["roomIndex"], "dps": dps})
        _rooms[i]["dps"] = dps

    avgs = {}
    for k, v in stages.items():
        total = sum(map(lambda x: x["dps"], v))
        avgs[k] = total / len(v)

    for k, v in stages.items():
        stages[k] = sorted(v, key=lambda x: x["dps"], reverse=True)

    return avgs, stages


def cutrule(room, stage_dps_avg, stage_dps_list, _last=None, _next=None):
    # _c0 = room["isRewind"] or (_last and _last["isRewind"])
    # if _c0: return True
    """
    ret True/False, 'reason':
    'rewind'
    'special'
    'seen'
    'floorfirst'
    'event'
    'dps'
    'default'
    """

    if room["isRewind"]:
        return True, "rewind"
    # if room["stage"] == 11:
    # print(room["name"], room["roomType"], flush=True)
    if room["roomType"] != "ROOM_DEFAULT":
        return False, "special"
    if not room["isFirstVisit"]:
        return True, "seen"

    if (not _last) or (_last["stage"] != room["stage"]):
        # keep all first rooms
        return False, "floorfirst"
    if not room["isHostile"] and len(room["events"]) == 0:
        # Remove rooms w/o enemies and events
        return True, "default"

    if room["stage"] >= 4 and not room["isHostile"]:
        for e in room["events"]:
            if e["id"] == "PICKUP_ITEM":  # or e["id"] == "TAKE_DAMAGE" or e["id"] == "PICKUP_HEART":
                return False, "event"

    if ("dps" in room.keys()):
        stage = room["stage"]
        stage_avg = stage_dps_avg[stage]
        toplist = stage_dps_list[stage]
        if len(toplist) > 2:
            toplist = toplist[:2]
        for v in toplist:
            if v["idx"] == r["roomIndex"]:
                return False, "dps"

        for e in room["events"]:
            if e["id"] == "PICKUP_ITEM":
                return False, "event"
        return True, "default"

    if room["stage"] >= 4 and (len(room["events"]) <= 2 or room["isHostile"]):
        return True, "default"

    return False, "default"


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

# exit()


if __name__ == '__main__':
    uncutruns = sorted(Path("./uncut").iterdir(), key=os.path.getmtime)
    run_name = Path(uncutruns[-1]).stem

    with open("./uncut/{}.json".format(run_name)) as f:
        info = json.load(f)

    vid_fname = info["vid_filename"]
    vid_p = Path(vid_fname)

    # print("Loading video ...", flush=True)
    # vid = VideoFileClip(vid_fname)
    # print("Video loaded: {}".format(vid_fname), flush=True)

    # outdir = "roomsout/{}TEST".format(run_name)
    # os.makedirs(outdir, exist_ok=True)
    # print("Outdir made: {}".format(outdir), flush=True)

    # print("Getting duration: {}".format(str(vid_p)))
    duration = ffprobe_duration(vid_p)
    # duration = None
    # duration = vid.duration
    # rooms = fixTimes(info["rooms"], info["obs_starttime"], duration)
    rooms = Rooms(info["rooms"], info["obs_starttime"], duration)

    # for i, r in enumerate(rooms):
    #     cleared = 0
    #     events = r["events"]
    #     for e in events:
    #         e["id"] = EventNames[e["id"]]
    #     r["events"] = events

    #     if len(events) > 0:
    #         cleared = events[-1]["time"]
    #     else:
    #         cleared = r["time"][1]

    #     r["cleared"] = 
    stage_dps_avg, stage_dps_rooms = calc_dpsavg(rooms)
    print("DPS AVERAGE PER STAGES")
    for k, v in stage_dps_avg.items():
        print("  {}: {}".format(k, v), flush=True)
        dpsroomlist = stage_dps_rooms[k]
        # for r in dpsroomlist:
        #     print("    {}: {}".format(r["idx"], r["dps"]), flush=True)
    # exit()

    keep_rooms = []
    keep_time = 0
    for i, r in enumerate(rooms):
        last_ = None if i == 0 else rooms[i - 1]
        next_ = None if i >= (len(rooms) - 1) else rooms[i + 1]
        # if r["stage"] == 11:
        # print("Cutting {}".format(r["name"]), flush=True)
        should_cut, reason = cutrule(r, stage_dps_avg, stage_dps_rooms, last_, next_)
        if should_cut: continue

        r["cutrule"] = reason
        if reason == "event":
            keep_rooms.append(r)
            continue
        else:
            # events = r["events"]
            # for e in events:
            # e["id"] = EventNames[e["id"]]
            # r["events"] = events
            cleared = 0

            if len(r["events"]) > 0:
                cleared = r["events"][-1]["time"] + CLEARED_END_PADDING
            elif r["time"][1]:
                cleared = r["time"][1]

            if r["time"][1] and cleared > r["time"][1]:
                cleared = r["time"][1]

            # r["ordid"] = i

            # r["cutrule"] = "keep"
            if i + 1 == len(rooms):
                cleared = r["time"][1]

            r["cleared"] = cleared

            keep_rooms.append(r)

            if cleared <= r["time"][0]:
                # this happens when ffprobe_duration couldn't give time
                print("CLEARED WEIRD: {} : {} - {}/{}".format(r["time"][0], cleared, i, len(rooms)), flush=True)
            # if cleared: # for cases where we can't get duration from ffprobe
            # keep_time += cleared - r["time"][0]
            # if len(keep_rooms) >= 13:
            # break

    # pprint(keep_rooms)

    cuts = []
    for i, r in enumerate(keep_rooms):
        should_fadein = True
        should_fadeout = True

        t0 = r["time"][0]
        if i == 0:
            should_fadein = False
            t0 = 0
        elif r["cutrule"] == "event":
            print("CUTRULE EVENT {} - {}".format(i, r["name"]))
            for j, e in enumerate(r["events"]):
                if e["id"] != "PICKUP_ITEM":  # and e["id"] != "PICKUP_HEART" and e["id"] != "TAKE_DAMAGE":
                    continue
                print("    {}".format(e["id"]), flush=True)
                t0 = e["time"] - EVENT_CUT_OFFSET
                t1 = e["time"] + EVENT_CUT_OFFSET
                cuts.append([t0, t1, should_fadein, should_fadeout])
            continue
        elif (r["_ord"] - 1) == keep_rooms[i - 1]["_ord"]:
            last_t1 = cuts[-1][1]
            if t0 - last_t1 <= DOORTRANSITION_WAIT_LIMIT:
                cuts[-1][1] = t0 - (frame_to_sec(1))
                cuts[-1][3] = False  # fadeout
                should_fadein = False
            else:
                t0 -= DOORTRANSITION_WAIT_COMPROMISE  # ROOM_START_OFFSET
        elif r["roomType"] == "ROOM_BOSS" and r["isFirstVisit"]:
            t0 += BOSS_START_OFFSET
        elif r["roomType"] == "ROOM_DEFAULT":
            t0 += ROOM_START_OFFSET
        else:
            # Make sure we show entering the room for item, curse, boss rooms etc
            t0 -= DOORTRANSITION_WAIT_COMPROMISE

        # If cut starts before last ends, concat them instead
        # if i > 0 and t0 <= cuts[i-1][1]:
        #     t0 = cuts[i-1][1] + frame_to_sec(1)
        #     cuts[i-1][3] = False
        #     should_fadein = False
        t1 = r["cleared"]

        # print("{}: {}".format(r["name"], t1-t0), flush=True)
        if (t1 - t0 > BOSS_ROOM_TIMELIMIT):
            print("> BOSS_ROOM_TIMELIMIT: {} | {} | {}".format(i, r["name"], r["roomType"]), flush=True)

            # This is meant for boss rush and hush
            t0_0 = t0
            # t1_0 = t0 + (BOSS_ROOM_TIMELIMIT / 2.0)
            # t0_1 = t1 - (BOSS_ROOM_TIMELIMIT / 2.0)
            t1_0 = t0 + BOSS_ROOM_TIMELIMIT_OFFSET  # (BOSS_ROOM_TIMELIMIT / 2.0)
            t0_1 = t1 - (BOSS_EVENT_CUT_OFFSET * 2)  # (BOSS_ROOM_TIMELIMIT / 2.0)
            t1_1 = t1
            print("   {} : {}".format(t0_0, t1_0))
            cuts.append([t0_0, t1_0, should_fadein, True])
            for e in r["events"]:
                et0 = e["time"] - BOSS_EVENT_CUT_OFFSET
                et1 = e["time"] + BOSS_EVENT_CUT_OFFSET
                if et1 <= t1_0: continue
                if et0 >= t0_1: break
                if e["id"] == "TAKE_DAMAGE":
                    cuts.append([et0, et1, True, True])
                    print("       {} : {}".format(et0, et1))
            print("   {} : {}".format(t0_1, t1_1), flush=True)
            cuts.append([t0_1, t1_1, True, should_fadeout])
        else:
            cuts.append([t0, t1, should_fadein, should_fadeout])

    ellided = []

    for i, c in enumerate(cuts):
        if i == 0:
            ellided.append(c)
            continue
        t0 = c[0]
        t1 = c[1]
        last_t0 = ellided[-1][0]
        last_t1 = ellided[-1][1]
        last_fadeout = ellided[-1][3]
        if t0 <= last_t1 or (not last_fadeout):
            ellided[-1][1] = t1
            ellided[-1][3] = c[3]
        else:
            ellided.append(c)

    # pprint(ellided)
    # exit()
    cuts = ellided

    cut_time = 0
    for c in cuts:
        c1 = c[1] if c[1] else c[0] + 20  # a guess
        cut_time += c1 - c[0]
        if c[2]: cut_time -= (FADE_DURATION / 4)
        if c[3]: cut_time -= (FADE_DURATION / 4)

    print(str(datetime.timedelta(seconds=cut_time)))

    print("Cutting {} clips.".format(len(cuts)), flush=True)
    t = time()

    # exit()
    # exit()
    # for i in range(60,len(cuts)):
    #     print("    {}".format(i))
    #     # pprint(keep_rooms[i])
    #     pprint(cuts[i])

    # pprint(rooms[-1])
    # print(cuts[56][3], flush=True)
    # print(cuts[57][2], flush=True)
    cvcut(cuts, vid_p, fade_duration=FADE_DURATION, total_frames=round(cut_time * 60), tmp_id=run_name)

    # print("Making cuts, no feedback.", flush=True)
    # mkcuts(vid_p, cuts, tmp_id=run_name)

    # print("Making crossfade.", flush=True)
    # xfade_conc(cuts, fade_duration=0.5, tmp_id=run_name)

    dt = time() - t
    print("Total time:  " + str(datetime.timedelta(seconds=dt)), flush=True)
    # exit()
