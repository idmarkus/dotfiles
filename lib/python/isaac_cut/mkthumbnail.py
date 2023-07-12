from pathlib import Path

import cv2 as cv
import numpy as np

from spriteedit import *
from rooms import Rooms

from pprint import pprint


def get_latest_run():
    from pathlib import Path
    import os
    import json
    from ffmpegtest import ffprobe_duration
    uncutruns = sorted(Path("./uncut").iterdir(), key=os.path.getmtime)
    run_name = Path(uncutruns[-2]).stem

    with open("./uncut/{}.json".format(run_name)) as f:
        info = json.load(f)

    vid_p = Path(info["vid_filename"])
    duration = ffprobe_duration(vid_p)
    return Rooms(info["rooms"], info["obs_starttime"], duration)


rooms = get_latest_run()
pprint(rooms.collectibles)
# exit()

item = trim(itemsprite(149))
altar = trim(altarsprite())

item = scale(item, 9)
altar = scale(altar, 7)

# item = cv.resize(item, (0,0),fx=5.0, fy=5.0, interpolation=cv.INTER_NEAREST)
bg = np.ones((720, 1280, 3), np.uint8) * 255


def get_random_backdrop():
    from random import randint
    d = Path("resources/backdrop/scaled")
    di = list(d.iterdir())
    p = di[randint(0, len(di) - 1)]
    im = cv.imread(str(p))  # , cv.IMREAD_UNCHANGED)
    return im


overlay_p = Path("resources/backdrop/scaled/overlay.png")
while True:
    bg = get_random_backdrop()
    overlay = cv.imread(str(overlay_p), cv.IMREAD_UNCHANGED)

    b_d = np.asarray(bg.shape[:2])
    a_d = np.asarray(altar.shape[:2])
    i_d = np.asarray(item.shape[:2])

    ac = (b_d // 2) - (a_d // 2)
    ic = (b_d // 2) - (i_d // 2)

    ih, iw = item.shape[:2]
    ah, aw = altar.shape[:2]
    bh, bw = bg.shape[:2]

    overlay_a(bg, altar, ac[1] - (ah * 0.008), ac[0] + (ih * 1.1))
    overlay_a(bg, item, ic[1], ic[0])
    overlay[:, :, 3] = overlay[:, :, 3] * 0.5
    overlay_a(bg, overlay, 0, 0)
    # cv.line(bg, (bw//2,0), (bw//2,bh), (0,0,255), 2)
    # cv.line(bg, (0,bh//2), (bw,bh//2), (0,0,255), 2)
    bg = scale(bg, 0.5)
    cv.imshow("im", bg)

    if cv.waitKey(0) & 0xFF == ord('q'):
        cv.destroyAllWindows()
        break
