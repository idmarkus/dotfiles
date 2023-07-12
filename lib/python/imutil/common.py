import numpy as np
import cv2 as cv


def ntile(img, size):
    # This will always overlap, even if (ih|iw)%size==0
    ih, iw = img.shape[:2]
    n = iw // size
    m = ih // size
    rest_w = iw % size
    rest_h = ih % size

    gap_w = int(round((size - rest_w) / n))
    gap_h = int(round((size - rest_h) / m))

    xs = [(x * size) - (x * gap_w) for x in range(n)] + [iw - size]
    ys = [(y * size) - (y * gap_h) for y in range(m)] + [ih - size]

    return [[x, y, x + size, y + size] for x in xs for y in ys]


def dhash(image, hashSize=8):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    resized = cv.resize(image, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def hammingDistance(x, y):
    """
    :type x: int
    :type y: int
    :rtype: int
    """
    ans = 0
    for i in range(63, -1, -1):
        b1 = x >> i & 1
        b2 = y >> i & 1
        ans += not (b1 == b2)
        # if not(b1==b2):
        # print(b1,b2,i)
    return ans


def median(im, ratio):
    kernel_ratio = 0.03
    largest_dim = im.shape[0] if im.shape[0] > im.shape[1] else im.shape[1]
    kernelsize = int(round(float(largest_dim) * kernel_ratio))
    if (kernelsize % 2 == 0): kernelsize += 1
    return cv.medianBlur(im, kernelsize)


def nmtile(img, w, h, overlapping=True):
    ih, iw = img.shape[:2]
    n = iw // w
    m = ih // h
    rest_w = iw % w
    rest_h = ih % h

    if (rest_w and overlapping):
        gap_w = (w - rest_w) // n
        xs = [(x * w) - (x * gap_w) for x in range(n)] + [iw - w]
    else:
        xs = [x * w for x in range(n)]

    if (rest_h and overlapping):
        gap_h = (h - rest_h) // m
        ys = [(y * h) - (y * gap_h) for y in range(m)] + [ih - h]
    else:
        ys = [y * h for y in range(m)]

    if (not overlapping) and rest_w: xs.append(iw - w)
    if (not overlapping) and rest_h: ys.append(ih - h)

    return [[x, y, x + w, y + h] for x in xs for y in ys]


def ntile1(img, size):
    ih, iw = img.shape[:2]
    n = iw // size
    m = ih // size
    rest_w = iw % size
    rest_h = ih % size

    if (rest_w):
        gap_w = round((size - rest_w) / n)
        xs = [(x * size) - (x * gap_w) for x in range(n)] + [iw - size]
        print("gap_w: ", gap_w)
    else:
        xs = [x * size for x in range(n)]

    if rest_h:
        gap_h = round((size - rest_h) / m)
        ys = [(y * size) - (y * gap_h) for y in range(m)] + [ih - size]
    else:
        ys = [y * size for y in range(m)]

    print(iw, ih, n, m, rest_w, rest_h)
    return [[x, y, x + size, y + size] for x in xs for y in ys]


def hamming_chk(img):
    largest_dim = img.shape[0] if img.shape[0] > img.shape[1] else img.shape[1]
    kernelsize = largest_dim // 2
    kernelsize = kernelsize - 1 if kernelsize % 2 == 0 else kernelsize
    median_im = cv.medianBlur(img, kernelsize)

    dist = hammingDistance(dhash(img), dhash(median_im))
    return dist
    # print(dist)
    # return dist > 5
