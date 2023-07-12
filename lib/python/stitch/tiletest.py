import cv2 as cv
import numpy as np


def tiletest(im, tilesize, overlap, div=1, interpolation=cv.INTER_CUBIC):
    if isinstance(tilesize, int): tilesize = (tilesize, tilesize)
    if isinstance(overlap, int): overlap = (overlap, overlap)

    tilesize_h, tilesize_w = tilesize
    overlap_w, overlap_h = overlap
    h, w = im.shape[:2]
    h //= div
    w //= div

    x0 = 0
    cx = []
    while x0 < (w - overlap_w):
        x1 = x0 + tilesize_w
        cx.append((x0, x1))
        x0 = x1 - overlap_w
        y0 = 0
        cy = []
    while y0 < (h - overlap_h):
        y1 = y0 + tilesize_h
        cy.append((y0, y1))
        y0 = y1 - overlap_h

    # x1, y1 is left as the overhang, so resize to fit uneven tiling
    # ensuring the tiles stay a fixed size
    if im is not None:
        im = cv.resize(im, (x1, y1), interpolation=interpolation)
    else:
        im = np.ones((y1, x1, 3), np.uint8) * 255

    nh = len(cy)
    nw = len(cx)
    # tiles = [im[y0:y1, x0:x1] for y0,y1 in cy for x0,x1 in cx]
    # return nh, nw, tiles
    cv.rectangle(im, (w, 0), (x1, y1), (0, 0, 255, 20), cv.FILLED)
    cv.rectangle(im, (0, h), (x1, y1), (0, 0, 255, 20), cv.FILLED)

    linewidth = 3
    for y0, y1 in cy:
        assert (y1 - y0 == tilesize_h)
        assert (y1 <= im.shape[0])
        for x0, x1 in cx:
            assert (x1 - x0 == tilesize_w)
            assert (x1 <= im.shape[1])
            # cv.rectangle(im,(x0,y0),(x1,y1),(0,255,255,255),3)
            cv.line(im, (x0, y0), (x1, y0), (255, 0, 0, 255), linewidth)
            cv.line(im, (x1, y0), (x1, y1), (0, 255, 255, 255), linewidth)
            cv.line(im, (x1, y1), (x0, y1), (0, 255, 255, 255), linewidth)
            cv.line(im, (x0, y1), (x0, y0), (255, 0, 0, 255), linewidth)
    return im


tilesize_h = 512
tilesize_w = 512
overlap_h = 32
overlap_w = 32

testim = cv.imread("testim_lr.png")
h, w = testim.shape[:2]
# blankim = np.ones((h,w,3), np.uint8) * 255

test = tiletest(testim, (tilesize_h, tilesize_w), (overlap_h, overlap_w), div=1)
test = cv.resize(test, (w // 4, h // 4))
cv.imshow("test", test)
key = cv.waitKey(0)
# if cv.waitKey(0) & 0xFF == ord('q'):
cv.destroyAllWindows()
