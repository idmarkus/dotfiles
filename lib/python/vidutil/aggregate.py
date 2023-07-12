import os
from os.path import splitext

import itertools
import mimetypes
from collections import namedtuple
from pathlib import Path
from multiprocessing import Pool
from functools import partial

import numpy as np
import cv2 as cv
import ffmpeg

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

ERROR = "\033[91mERROR:\033[0m "


def flatmap(func, *iterable):
    return itertools.chain.from_iterable(map(func, *iterable))


MimeTFile = namedtuple('MimeTFile', ['path', 'mime'])


# def ff(p):
#     if p.exists():
#         if p.is_dir():
#             return flatmap(ff, p.iterdir())
#         mime_t = mimetypes.guess_type(p)[0][:5]
#         if mime_t == "video" or mime_t == "image":
#             return [MimeTFile(p, mime_t)]
#     print(ERROR + "\'{}\' is not a valid directory, image or video.".format(str(p)))
#     return []
# t2 = flatmap(ff, a)
# print(next(t2))
# print(next(t2))
# print(next(t2))


class IterFrames():
    # Nested frame-iterator - single-threaded, inoptimal, convenient
    class itframes_iter:
        def __init__(self, xs):
            self.xs = xs;
            self.cap = None;

        def __iter__(self):
            return self;

        def __next__(self):
            if self.cap:  # Early-catch vidcap
                ret, frame = self.cap.read()
                if ret: return frame
                # fallthrough if cap failed or finished
                self.cap.release();
                self.cap = None

            try:
                active = next(self.xs)  # Get next x from xs
            except StopIteration:
                raise  # done, we've seen all xs

            if active.mime == "video":
                self.cap = cv.VideoCapture(str(active.path))
                if not self.cap.isOpened(): self.cap = None
                # either way, fallthrough to return __next__()    
            else:  # mime is "image"
                img = cv.imread(str(active.path))
                # Check that img is not empty or None (size=1)
                if np.asarray(img).size > 1: return img

            # img failed or new cap
            return self.__next__()

    '''
    Iterable allowing arbitrary arguments of filepath strings to vid/img files/folders:
      IterFrames("vid.mp4")
      IterFrames("~/images")
      IterFrames(["vid.mp4", "~/images"])
      IterFrames("filenames.txt") # only newline-separated for now
    or going full brain:
      IterFrames(["0.mp4"], "~/folder", ["frames/00.png", "x.mov", "list.txt"])

    TODO: Add support for URLs / stream / YT-download, etc
    '''

    def __init__(self, arg, *args):
        if not isinstance(arg, list): arg = [arg]
        self.xs = flatmap(self.ff, [Path(x).expanduser() for x in [*arg, *args]])
        self._n_frames = self._xs_vid = self._xs_img = None

    def __iter__(self):
        return self.itframes_iter(self.xs)

    # Function to disambiguate filepaths, flatmapping directory globs, etc
    def ff(self, p):
        if isinstance(p, str):
            p = Path(p).expanduser()
        if p.exists():
            # If-nested so we can fallthrough to error handling if things fail
            if p.is_dir():
                # Recurse over directory contents (incl. subdirectories)
                return flatmap(self.ff, p.iterdir())
            # Check mimetype, 5-length string is arbitrary, output looks like "video/mp4"
            mime_t = mimetypes.guess_type(p)[0][:5]
            if mime_t == "video" or mime_t == "image":
                return [MimeTFile(p, mime_t)]  # recursion end-point
            elif mime_t == "text/":
                # Check if we have a list of filenames, if so, recurse as if directory
                with open(p, 'r') as f:
                    lines = [Path(x.strip()).expanduser() for x in f.readlines()]
                    # pre-check valid files to avoid excessive calls
                    lines = [x for x in lines if x.exists()]
                if len(lines) > 0:
                    return flatmap(self.ff, lines)
                # else fallthrough: len(lines) > 0
            # else fallthrough: mime_t != "video" != "image" != "text/"
        print(ERROR + "\'{}\' is not a valid directory, filename list, image or video.".format(str(p)))
        return []

    def n_frames(self):
        # Only count once
        if self._n_frames: return self.n_frames
        if not self._xs_vid: self._sort_types()
        vcount = 0
        for path in self._xs_vid:
            cap = cv.VideoCapture(str(path))
            if not cap.isOpened(): continue  # we should remove here as well
            vcount += int(cap.get(cv.CAP_PROP_FRAME_COUNT))

        self._n_vframes = vcount
        self._n_frames = vcount + len(self._xs_img)

        return self._n_frames

    def _sort_types(self):
        # For batch-processing we need to know,
        # for normal iterator usage, we do not
        xvids = set()
        ximgs = set()
        for path, mime in self.xs:
            if mime == "video":
                xvids.add(path)
            else:
                ximgs.add(path)
        self._xs_vid = list(xvids)
        self._xs_img = list(ximgs)
        # self.xs = itertools.chain(self._xs_vid, self._xs_img)

    def batch(self, func, n_workers=4):
        # This also sorts by type
        frames = self.n_frames()

        # First process videos, max 1 thread per video
        nvs = len(self._xs_vid)
        nv_workers = nvs if nvs < n_workers else n_workers

        _proc_vid_partial = partial(_proc_vid, func)
        _proc_img_partial = partial(_proc_img, func)
        _chunksize = int(len(self._xs_img) / n_workers)
        retvid = False
        retimg = False
        try:
            with Pool(processes=n_workers) as pool:
                retvid = pool.apply_async(_proc_vid_partial, self._xs_vid)
                retimg = all(pool.imap_unordered(_proc_img_partial, self._xs_img, chunksize=_chunksize))
                retvid = retvid.get()
        except:
            raise
        print(retvid, retimg)
        # if nv_workers > 0:
        #     try:
        #         with Pool(processes=nv_workers) as pool:
        #             retvid = pool.map_async(_proc_vid_partial, self._xs_vid)
        #             # ret = pool.imap_unordered(_proc_vid, self._xs_vid)
        #     except: raise
        # try:
        #     with Pool(processes=n_workers) as pool:
        #         retimg = pool.map(partial(_proc_img, func), self._xs_img, chunksize=int(len(self._xs_img)/n_workers))
        #         # pool.imap_unordered(func, self._xs_img)
        # except:
        #     raise
        # print(retvid, retimg)


def _proc_vid(_func, filename):
    cap = cv.VideoCapture(str(filename))
    if not cap.isOpened(): cap.release(); return False;
    while True:
        ret, frame = cap.read()
        if not ret: cap.release(); break;
        _func(frame)
    return True


def _proc_img(_func, filename):
    frame = cv.imread(str(filename))
    if np.asarray(frame).size <= 1: return False
    _func(frame)
    return True


a = [Path(x).expanduser() for x in ["list.txt"]]
# b = IterFrames("list.txt")
b = IterFrames(a)


# print(b.n_frames())

def batch_testf(frame):
    return frame.shape[1] + os.getpid()
    # print(frame.shape, os.getpid())


# b.batch(batch_testf)

# frames = b.n_frames()
def pooled():
    ret = 0
    with Pool(processes=4) as pool:
        ret = pool.map(batch_testf, b.__iter__(), chunksize=int(frames / 4))
    return ret


def unpooled():
    return all(map(batch_testf, b))
    ret = 0
    for frame in b:
        ret = batch_testf(frame)
    return ret
    # ret = map(batch_testf, b)
    # return all(ret)


def pool_batched():
    return b.batch(batch_testf, n_workers=8)


import timeit

print(timeit.timeit(pool_batched, number=2))
# for i, frame in enumerate(b):
# print(i)
