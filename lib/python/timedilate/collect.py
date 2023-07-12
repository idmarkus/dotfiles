import numpy as np
import cv2 as cv

from pathlib import Path
import os

out = cv.VideoWriter('result.avi', cv.VideoWriter_fourcc(*'DIVX'), 25, (640, 360))

# frames = os.listdir("output")
# print(frames[:5])
# frames = [str(p) for p in Path("output").listdir()]

for i in range(1742):
    if i % 20 == 0: print(i, flush=True)
    frame = cv.imread("output/{}.jpg".format(i))
    out.write(frame)

out.release()
