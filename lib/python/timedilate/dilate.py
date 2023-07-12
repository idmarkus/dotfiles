from pathlib import Path
import atexit

import math

import numpy as np
import cv2 as cv


class Framekeep():
    frames = None
    fps = 0
    nframes = 0

    def __init__(self, video, verbal=False):

        if not isinstance(video, cv.VideoCapture):
            cap = cv.VideoCapture(str(video))
        else:
            cap = video

        self.fps = cap.get(cv.CAP_PROP_FPS)
        cn = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        cw = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        ch = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        frames = np.zeros((cn, ch, cw, 3), np.uint8)

        if verbal:
            print("Reading frames: {}".format(cn), flush=True)

        n = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if verbal and n % 15 == 0: print("\tread: {}".format(n), flush=True)
            if not ret: break
            frames[n] = frame
            n += 1

        cap.release()
        self.frames = frames
        self.nframes = cn

    def at_second(self, second):
        n = round(self.fps * second);
        if (n >= self.nframes):
            n = nframes - 1
        return self.frames[n]

    def at_percent(self, weight):
        if (weight > 1.0 and weight < 100):
            weight = weight / 100.0
        n = round(self.nframes * weight)
        return self.frames[n]


class Atoms():
    times = None
    deltas = None
    framekeep = None
    update_norm = 0.0
    norm_t = 0.0
    n = 0

    def __init__(self, framekeep):
        self.framekeep = framekeep
        self.shape = framekeep.frames[0].shape

        self.times = np.zeros(self.shape[:2], np.float)
        self.deltas = np.zeros(self.shape[:2], np.float)

        self.update_norm = 1.0 / framekeep.fps

    def construct(self):
        im = np.zeros(self.shape, np.uint8)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                frame = self.framekeep.at_second(self.times[i, j])
                im[i, j] = frame[i, j]
        return im

    def update(self):
        self.delta_step_A()

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                self.times[i, j] += (self.deltas[i, j] * self.update_norm)
        self.norm_t += 1.0 * self.update_norm

    def delta_step_A(self):
        for i in range(self.shape[0]):
            iw = i / self.shape[0]
            for j in range(self.shape[1]):
                jw = j / self.shape[1]

                di = math.sin((iw + jw) * self.n)
                # dj = math.sin(jw * self.n)

                self.deltas[i, j] = (di + 1.0) / 2.0

        self.n += 1


class DeltaProgram():
    deltas = None
    framekeep = None
    update_norm = 0.0
    norm_t = 0.0
    n = 0

    def __init__(self, framekeep):
        self.framekeep = framekeep
        self.shape = framekeep.frames[0].shape
        self.deltas = np.zeros(self.shape[:2], np.float)
        self.update_norm = 1.0 / framekeep.fps

    def vis(self):
        im = np.zeros(self.shape, np.uint8)
        # for i, j in zip(range(self.shape[0]), range(self.shape[1])):
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                w = (self.deltas[i, j] + 1.0) / 2.0
                im[i, j] = np.uint8(w * 255.0)
        return im

    def step(self):
        for i in range(self.shape[0]):
            iw = i / self.shape[0]
            for j in range(self.shape[1]):
                jw = j / self.shape[1]

                di = math.sin((iw + jw) * self.n)
                # dj = math.sin(jw * self.n)

                self.deltas[i, j] = di

        self.n += 1
        # norm_t += 1.0 * update_norm


def main():
    testvid_p = Path("testvid.mp4")
    out_p = Path("output")
    out_p.mkdir(exist_ok=True)

    frames = Framekeep(testvid_p)
    atoms = Atoms(frames)
    # dp = DeltaProgram(frames)

    while True:
        # print(atoms.times[0], flush=True)
        atoms.update()
        # print(dp.deltas[0], flush=True)
        im = atoms.construct()
        if atoms.n >= frames.nframes:
            break

        cv.imwrite("output/{}.jpg".format(atoms.n), im)
        # cv.imshow("im", im)
        # if cv.waitKey(1) & 0xFF == ord('q'):
        # break
    # im = dp.vis()

    # cv.imshow("im", im)
    # cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
