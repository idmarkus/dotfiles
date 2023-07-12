import os
from os.path import splitext

from pathlib import Path

import numpy as np
import cv2 as cv

'''
Aggregate reader.

Disambiguate input:
  1 vid path: "~/video.mp4"
  1 img path: "~/image.png"
  1 dir path: "~/frames"
    with multiple images: "~/frames" -> ["~/frames/000.png", ..., "~/frames/nnn.png"]
    with multiple videos: "~/videos" -> ["~/videos/videoA.mp4", ..., "~/videos/videoN.avi"]
    with deepdive mixed:  "~/indata" -> ["~/indata/i.png", "~/indata/v.avi", "~/indata/vids/a.mp4", "~/indata/frames/000.png"]
                                       [x for x in "~/indata/**/*" if isvid(x) or isimg(x)]
  list of mixed paths: ["~/videos/a.mp4","~/images/b.png", "~/frames", "~/indata"]
  TODO: add URL support: "https://youtu.be/NNNNNNN", "example.com/image.png", ...

2. Return iterable of frames:
   Ordered, at least for ordered input (e.g. "frames/000.png", ..., ".../nnn.png")
     input   = Aggregate(["vid.mp4", "~/media", ~/pretreated/frames])
     nframes = input.n_frames

     # Direct seek -- this could be messy to implement, but ffmpeg
     # has direct seek and static frameinfo for videos, at least
     frame   = input[485]

     # As iterable
     for frame in input:
       show(frame)

     # Batch output
     input.map(transforms)
     input.batchWrite("output/frames", "Xn.png") # Where 'X' would be the original name, 'n' UUIDifying, maybe?

'''

IMG_EXT = ["bmp", "dib", "jpeg", "jpg", "jp2", "png", "pbm", "pgm", "ppm", "sr", "ras", "tiff", "tif"]
IMG_EXT = [x.upper() for x in IMG_EXT] + IMG_EXT


def fext_nodot(x):
    return splitext(x)[1][1:]


class InvalidFile(Exception):
    def __init__(self, expr, msg):
        self.expression = expr
        self.message = "\033[91mERROR:\033[0m " + msg


class FrameCapture:
    _isVideoCapture = False
    _ind = 0

    def __init__(self, x):
        # Accept video/image filename, directory with images, or (eventually) streamable URL
        try:
            # Since 'x' can be an integer for webcam capture, we just duck-type it
            if x == '0' or x == '1' or x == '2':
                # XXX: Webcam indexes can go higher, this is dumb
                x = int(x)

            self._cap = cv.VideoCapture(x)
            if not self._cap.isOpened():
                if isinstance(x, int):
                    raise InvalidFile(x, "\'{}\' is not a valid camera index".format(x))
                else:
                    raise InvalidFile(x, "\'{}\' is not a valid file or directory".format(x))

            self._isVideoCapture = True
        except InvalidFile as e:
            if isinstance(x, int):
                print(e.message)
                raise

            p = Path(x).expanduser()
            if not p.exists():
                print(e.message)
                raise

            self._ind = 0
            if p.is_dir():
                self._frames = [f for f in p.iterdir() if splitext(f)[1][1:] in IMG_EXT]
                if not self._frames or len(self._frames) < 1:
                    print("\033[91mERROR:\033[0m " + "Directory contains no valid image files: \'{}\'".format(x))
                    raise
            elif p.is_file() and fext_nodot(x) in IMG_EXT:
                self._frames = [p]
            else:
                print(e.message)
                raise

    def read(self):
        if self._isVideoCapture:
            return self._cap.read()

        if self._ind >= len(self._frames):
            return False, None
        else:
            self._ind += 1
            return True, np.asarray(cv.imread(str(self._frames[self._ind - 1])))

    def release(self):
        if self._isVideoCapture:
            self._cap.release()

# def main():
#     # print(IMG_EXT)
#     # return
#     import sys
#     fr = FrameCapture(sys.argv[1])
#     # print(fr._isVideoCapture, fr._cap.isOpened())

#     ret, frame = fr.read()
#     print(ret)

#     fr.release()

# if __name__ == "__main__":
#     main()
