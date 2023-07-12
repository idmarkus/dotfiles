# @title (new tiling) Stitch
import numpy as np
import cv2 as cv

from PIL import Image


class Stitch:
    def __init__(self, im, tilesize, overlap, div=1, interpolation=cv.INTER_CUBIC):
        if isinstance(tilesize, int): tilesize = (tilesize, tilesize)
        if isinstance(overlap, int): overlap = (overlap, overlap)
        assert (overlap[0] < tilesize[0])
        assert (overlap[1] < tilesize[1])

        if isinstance(im, Image.Image):
            self.isPIL = True
            im = np.asarray(im)
        else:
            self.isPIL = False

        self.tilesize = tilesize
        self.overlap = overlap

        self.div = div
        self._orig_shape = im.shape
        self.interpolation = interpolation

        self.tile(im, interpolation=interpolation)
        self.ntiles = len(self.tiles)

    def _disambig_key(self, key):
        if isinstance(key, int):
            return key
        else:
            x, y = key
            x = self.nw + x if x < 0 else x
            y = self.nh + y if y < 0 else y
            return (y * self.nw) + x

    def __getitem__(self, key):
        return self.tiles[self._disambig_key(key)]

    def __setitem__(self, key, val):
        self.tiles[self._disambig_key(key)] = val

    def __iter__(self):
        return self.tiles.__iter__()

    def __next__(self):
        return self.tiles.__next__()

    def tile(self, im, interpolation=cv.INTER_CUBIC):
        th, tw = self.tilesize
        lh, lw = self.overlap
        div = self.div

        h, w = im.shape[:2]
        h //= div
        w //= div

        x0 = 0
        cx = []
        while x0 < (w - lw):
            x1 = x0 + tw
            cx.append((x0, x1))
            x0 = x1 - lw
        y0 = 0
        cy = []
        while y0 < (h - lh):
            y1 = y0 + th
            cy.append((y0, y1))
            y0 = y1 - lh

        # x1, y1 is left as the overhang, so resize to fit uneven tiling
        # ensuring the tiles stay a fixed size
        im = cv.resize(im, (x1, y1), interpolation=interpolation)
        self.reshape = (y1, x1, im.shape[2])

        self.nh = len(cy)
        self.nw = len(cx)
        if self.isPIL:
            self.tiles = [Image.fromarray(im[y0:y1, x0:x1]) for y0, y1 in cy for x0, x1 in cx]
        else:
            self.tiles = [im[y0:y1, x0:x1] for y0, y1 in cy for x0, x1 in cx]
        # self.coord = [(y0,y1,x0,x1) for y0,y1 in cy for x0,x1 in cx]

    def mkmasks(self, maskshape, exp=2):
        """
        exp controls linearity, exp=1 is linear
                                exp=2 is perceptual
                                3 is cubic, etc 
        """

        # Make line strips for both masks (hori, vert)
        maskh, maskw = maskshape
        th, tw = self.tilesize
        maskx = np.zeros((1, maskw), np.float32)
        masky = np.zeros((maskh, 1), np.float32)

        halfw = maskw // 2
        halfh = maskh // 2

        # Multiplicants
        ww = maskw ** exp
        hh = maskh ** exp

        for x in range(maskw):
            vx = (x ** exp) / ww
            maskx[0, x] = vx
        for y in range(maskh):
            vy = (y ** exp) / hh
            masky[y, 0] = vy

        # Now resize linestrips to their final shape
        origw = self.reshape[1]
        maskx = cv.resize(maskx, (maskw, th), interpolation=cv.INTER_NEAREST)
        masky = cv.resize(masky, (origw, maskh), interpolation=cv.INTER_NEAREST)

        # maskx = np.reshape(np.repeat(maskx,3), (th, maskw, 3))
        # masky = np.reshape(np.repeat(masky,3), (maskh, maskw*2, 3))
        # masky = np.tile(masky, (1,(self.nw // 2) + 1,1))
        # Premult and convert
        maskx = cv.cvtColor(maskx, cv.COLOR_GRAY2BGR)
        masky = cv.cvtColor(masky, cv.COLOR_GRAY2BGR)
        return maskx, masky

    def blend(self, exp=1):
        def alphaBlend(im0, im1, mask):
            return cv.convertScaleAbs(im0 * (1 - mask) + im1 * mask)

        th, tw = self.tilesize
        lh, lw = self.overlap
        h, w, c = self.reshape
        mask, maskv = self.mkmasks(self.overlap, exp=exp)

        if self.isPIL:
            for i, tile in enumerate(self):
                self[i] = np.asarray(tile)

        merge = np.zeros((h, w, c), np.uint8)
        for j in range(self.nh):
            row1 = np.zeros((th, w, c), np.uint8)
            row1[:, :lw] = self[0, j][:, :lw]
            x0 = lw
            for i in range(self.nw - 1):
                x1 = x0 + tw - (lw * 2)
                row1[:, x0:x1] = self[i, j][:, lw:-lw]
                overlap0 = self[i, j][:, -lw:]
                overlap1 = self[i + 1, j][:, :lw]
                x0 = x1 + lw
                row1[:, x1:x0] = alphaBlend(overlap0, overlap1, mask)
            row1[:, x0:] = self[-1, j][:, lw:]
            if j == 0:
                merge[:lh, :] = row1[:lh, :]
                y0 = lh
            else:
                y1 = y0 + th - (lh * 2)
                merge[y0:y1, :] = row0[lh:-lh, :]
                overlap0 = row0[-lh:, :]
                overlap1 = row1[:lh, :]
                y0 = y1 + lh
                merge[y1:y0] = alphaBlend(overlap0, overlap1, maskv)
            row0 = row1

        merge[-(th - lh):, :] = row0[lh:, :]
        if self.isPIL:
            return Image.fromarray(merge)
        else:
            return merge
