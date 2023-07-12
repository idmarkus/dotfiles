from stitch2 import Stitch
import numpy as np
import cv2 as cv

from PIL import Image

exp = 1
test_n = 5
tile_h, tile_w = (512, 512)
overlap = 64

from pathlib import Path
import random
from time import perf_counter

inputs_d = Path("./testim")
inputs_p = [p for p in inputs_d.iterdir()]

random.shuffle(inputs_p)

# VAR_CUTOFF = 0.001
VAR_CUTOFF = 75
morph_size = 25


def texture_var(im):
    # canny = cv.Canny(im, 100, 200)
    # return np.mean(canny)
    return np.var(im)


# elem = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*morph_size + 1, 2*morph_size+1), (morph_size, morph_size))
#      diff = cv.morphologyEx(tile, cv.MORPH_OPEN, elem)
#      diff = tile - diff
#      var = np.var(diff)
#      return var
# return np.var(im)

perf_time = 0
perf_count = 0

for input_p in inputs_p:
    # if "441386" not in input_p.stem: continue
    testim = cv.imread(str(input_p))
    # testim = cv.cvtColor(testim, cv.COLOR_BGR2RGB)
    # testim = Image.fromarray(testim)

    # testim = np.asarray(testim)
    stitch = Stitch(testim, (tile_h, tile_w), overlap, div=1)

    # testim = cv.resize(testim, None, fx=0.5, fy=0.5)
    # stitch = Stitch(testim, (tile_h//2, tile_w//2), overlap//2, div=1)

    t = perf_counter()

    saved_tiles = 0
    highest = 0
    for k, tile in enumerate(stitch):
        # hsl = cv.cvtColor(tile, cv.COLOR_RGB2YUV)
        var = texture_var(tile)
        # var = np.var(tile)
        if var < VAR_CUTOFF:
            if var > highest: highest = var
            saved_tiles += 1
            propo = var / VAR_CUTOFF
            stitch[k] = np.ones_like(tile, np.uint8) * np.asarray([255, 0, int(255 * propo)])

    perf_time += perf_counter() - t
    perf_count += 1
    print(f"avg: {perf_time / perf_count}s\t{highest}\t({saved_tiles})  {saved_tiles * 2.20}s", flush=True)

    merge = stitch.blend(exp=exp)
    merge = cv.resize(merge, None, fx=0.15, fy=0.15)
    cv.imshow('im', merge)
    if cv.waitKey(0) & 0xFF == ord('q'):
        break
exit()

while test_n > 0:
    k = random.randint(0, len(stitch.tiles) - 1)
    tile = stitch[k]

    # var = np.var(tile)
    # if var < 25: continue
    # if var > 40: continue
    # if var < 100: continue
    elem = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2 * morph_size + 1, 2 * morph_size + 1),
                                    (morph_size, morph_size))
    diff = cv.morphologyEx(tile, cv.MORPH_OPEN, elem)
    diff = tile - diff
    var = np.var(diff)
    if var > 20: continue
    # diff = cv.close(tile, elem)
    print(var.shape)
    print(var, flush=True)
    print(np.var(diff), flush=True)
    cv.imshow("im", tile)
    cv.imshow("im2", diff)
    if cv.waitKey(0) & 0xFF == ord('q'):
        break
