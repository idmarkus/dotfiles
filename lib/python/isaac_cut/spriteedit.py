from pathlib import Path
import cv2 as cv
import numpy as np


def altarsprite():
    return cv.imread("resources/altar.png", cv.IMREAD_UNCHANGED)


def itemsprite(item_id, with_altar=False):
    p = Path("resources/collectibles") / f"{item_id:03}.png"
    if not p.exists():
        print("ERR: itemsprite() with invalid item_id: {}".format(item_id), flush=True)
        p = Path("resources/collectibles/placeholder.png")

    # cv.IMREAD_UNCHANGED to keep alpha channel
    im = cv.imread(str(p), cv.IMREAD_UNCHANGED)

    # if with_altar:
    #     # altar = cv.imread("resources/altar.png", cv.IMREAD_UNCHANGED)
    #     altar = altarsprite()
    #     newim = np.zeros((64,32,4), np.uint8)
    #     newim[:32,:] = im
    #     newim[32:,:] = altar
    #     return newim
    # im[:, :trim_l, :] = [0,0,255,255]
    # im[:, -trim_r:, :] = [0,0,255,255]
    return im


def trim(im):
    trim_l = None
    trim_r = None
    trim_t = None
    trim_b = None
    for i in range(32):
        if (not trim_l) and np.any(im[:, i, 3]):
            print(f"trim_l {i}", flush=True)
            trim_l = i

        if (not trim_r) and np.any(im[:, -i, 3]):
            print(f"trim_r {i}", flush=True)
            trim_r = (i - 1)

        if (not trim_t) and np.any(im[i, :, 3]):
            trim_t = i

        if (not trim_b) and np.any(im[-i, :, 3]):
            trim_b = (i - 1)
    return im[trim_t:-trim_b, trim_l:-trim_r, :]


def overlay_a(background, foreground, x_offset=None, y_offset=None):
    """
    From Ben on Stackexchange:
    https://stackoverflow.com/questions/40895785/using-opencv-to-overlay-transparent-image-onto-another-image
    """
    bg_h, bg_w, bg_channels = background.shape
    fg_h, fg_w, fg_channels = foreground.shape

    assert bg_channels == 3, f'background image should have exactly 3 channels (RGB). found:{bg_channels}'
    assert fg_channels == 4, f'foreground image should have exactly 4 channels (RGBA). found:{fg_channels}'

    # center by default
    if x_offset is None: x_offset = (bg_w - fg_w) // 2
    if y_offset is None: y_offset = (bg_h - fg_h) // 2

    x_offset = round(x_offset)
    y_offset = round(y_offset)

    w = min(fg_w, bg_w, fg_w + x_offset, bg_w - x_offset)
    h = min(fg_h, bg_h, fg_h + y_offset, bg_h - y_offset)

    if w < 1 or h < 1: return

    # clip foreground and background images to the overlapping regions
    bg_x = max(0, x_offset)
    bg_y = max(0, y_offset)
    fg_x = max(0, x_offset * -1)
    fg_y = max(0, y_offset * -1)
    foreground = foreground[fg_y:fg_y + h, fg_x:fg_x + w]
    background_subsection = background[bg_y:bg_y + h, bg_x:bg_x + w]

    # separate alpha and color channels from the foreground image
    foreground_colors = foreground[:, :, :3]
    alpha_channel = foreground[:, :, 3] / 255  # 0-255 => 0.0-1.0

    # construct an alpha_mask that matches the image shape
    alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

    # combine the background with the overlay image weighted by alpha
    composite = background_subsection * (1 - alpha_mask) + foreground_colors * alpha_mask

    # overwrite the section of the background image that has been updated
    background[bg_y:bg_y + h, bg_x:bg_x + w] = composite


def scale(im, fxy, interpolation=cv.INTER_NEAREST):
    h, w = im.shape[:2]
    nh = round(h * fxy)
    nw = round(w * fxy)
    return cv.resize(im, (nw, nh), interpolation=interpolation)
