import numpy as np
import cv2 as cv


def dbg_imshow(arg, *args):
    if not isinstance(arg, list): arg = [arg]
    for i, im in enumerate([*arg, *args]):
        cv.imshow(f"dbg{i}", im)
    return cv.waitKey(0) & 0xFF == ord('q')


def alphaBlend(im0, im1, mask):
    # if mask.ndim==3 and mask.shape[-1] == 3:
    #     alpha = mask/255.0
    # else:
    #     alpha = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)/255.0
    # alpha = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
    alpha = mask
    return cv.convertScaleAbs(im0 * (1 - alpha) + im1 * alpha)


def mkMasks(tilesize):
    mask = np.zeros((tilesize, tilesize), np.float)
    maskv = mask.copy()
    _half = tilesize // 2
    for x in range(tilesize):
        for y in range(tilesize):
            if x > _half:
                mask[y, x] = np.float(tilesize - x) / np.float(_half)
            else:
                mask[y, x] = np.float(x) / np.float(_half)

            if y > _half:
                maskv[y, x] = np.float(tilesize - y) / np.float(_half)
            else:
                maskv[y, x] = np.float(y) / np.float(_half)
    mask = np.reshape(np.repeat(mask, 3), (tilesize, tilesize, 3))
    maskv = np.reshape(np.repeat(maskv, 3), (tilesize, tilesize, 3))

    return mask, maskv


# def blendTiles(tiles):
#     tilesize = tiles.shape[2] # assume square tiles
#     assert(tiles.shape[2] == tiles.shape[3])
#     mask, maskv = mkMasks(tilesize)
#     mask = (mask * 255).astype(np.uint8)
#     maskv = (maskv * 255).astype(np.uint8)
#     rows, cols = tiles.shape[:2]
#     newrows = (rows // 2) + 1
#     newcols = (cols // 2) + 1
#     new_rows = np.zeros((tilesize * rows, tilesize * newcols, 3), np.uint8)
#     for r in range(rows):
#         y0 = r * tilesize
#         y1 = y0 + tilesize
#         new_rows[y0:y1, :tilesize] = tiles[r, 0]
#         for c in range(cols // 2):
#             cc = c*2
#             t0 = tiles[r, cc]
#             t1 = tiles[r, cc+2]
#             mid = tiles[r, cc+1]
#             tt = np.concatenate((t0[:, (tilesize//2):], t1[:, :(tilesize//2)]), axis=1)
#             blend = alphaBlend(tt, mid, mask)
#             x0 = (c * tilesize) + (tilesize//2)
#             x1 = x0 + tilesize
#             new_rows[y0:y1, x0:x1] = blend
#         new_rows[y0:y1, -(tilesize//2):] = tiles[r, -1][:, -(tilesize//2):]

#     newtiles = np.zeros((rows, newcols, tilesize, tilesize, 3), np.uint8)
#     for y in range(rows):
#         for x in range(newcols):
#             x0 = x * tilesize
#             x1 = x0 + tilesize
#             y0 = y * tilesize
#             y1 = y0 + tilesize
#             newtiles[y,x] = new_rows[y0:y1, x0:x1]

#     new = np.zeros((tilesize * newrows, tilesize*newcols, 3), np.uint8)
#     for c in range(newcols):
#         x0 = c * tilesize
#         x1 = x0 + tilesize
#         new[:tilesize, x0:x1] = newtiles[0, c]
#         for r in range(rows // 2):
#             rr = r*2
#             t0 = newtiles[rr, c]
#             t1 = newtiles[rr+2, c]
#             mid = newtiles[rr+1, c]
#             tt = np.concatenate((t0[(tilesize//2):, :], t1[:(tilesize//2), :]), axis=0)
#             blend = alphaBlend(tt, mid, maskv)
#             y0 = (r * tilesize) + (tilesize//2)
#             y1 = y0 + tilesize
#             new[y0:y1, x0:x1] = blend
#         new[-(tilesize//2):, x0:x1] = newtiles[-1, c][-(tilesize//2):, :]
#     return new

def alphaBlend(im0, im1, mask):
    return cv.convertScaleAbs(im0 * (1 - mask) + im1 * mask)


class Stitch:
    def __init__(self, im, tilesize=128, slicesize=128, interpolation=cv.INTER_NEAREST):
        self.tilesize = tilesize
        self.slicesize = slicesize
        self._orig_shape = im.shape
        self.interpolation = interpolation

        self._tiles = self.tile(im)

    def tile(self, im_):
        assert (len(im_.shape) == 3)
        h, w, nchannels = im_.shape
        tilesize = self.tilesize
        slicesize = self.slicesize

        # To ensure even tiling we scale the image to: ceil(w|h / tilesize) * tilesize
        from math import ceil
        nh = ceil(h / tilesize)
        nw = ceil(w / tilesize)
        scaleh = nh * tilesize
        scalew = nw * tilesize
        im = cv.resize(im_,
                       (scalew, scaleh),
                       interpolation=cv.INTER_LANCZOS4)
        print(scalew, scaleh)
        self._scale_shape = (scaleh, scalew, nchannels)
        # To make tiles overlap by tilesize/2
        th = (nh * 2) - 1
        tw = (nw * 2) - 1
        print(nh, th, (th // 2) + 1, flush=True)
        print(nw, tw, (tw // 2) + 1, flush=True)

        tiles = np.zeros((th, tw, slicesize, slicesize, nchannels), np.uint8)

        _half = tilesize // 2
        for y in range(th):
            for x in range(tw):
                x0 = x * _half
                y0 = y * _half
                x1 = x0 + tilesize
                y1 = y0 + tilesize

                tiles[y, x] = im[y0:y1, x0:x1] if tilesize == slicesize else cv.resize(im[y0:y1, x0:x1],
                                                                                       (slicesize, slicesize),
                                                                                       interpolation=self.interpolation)
        return tiles

    def mkmasks(self):
        masksize = self.slicesize // 2
        mask = np.zeros((masksize * 2, masksize), np.float)
        maskv = np.zeros((masksize, masksize * 2), np.float)
        _half = masksize // 2
        for x in range(masksize):
            dx = x if (x < _half) else masksize - x
            vx = np.float(dx) / np.float(_half)
            for y in range(masksize):
                dy = y if (y < _half) else masksize - y
                vy = np.float(dy) / np.float(_half)

                mask[y * 2, x] = mask[(y * 2) + 1, x] = vx
                maskv[y, x * 2] = maskv[y, (x * 2) + 1] = vy

        mask = np.reshape(np.repeat(mask, 3), (masksize * 2, masksize, 3))
        maskv = np.reshape(np.repeat(maskv, 3), (masksize, masksize * 2, 3))
        maskv = np.tile(maskv, (1, (self._tiles.shape[1] // 2) + 1, 1))

        return mask, maskv

    def blend(self):
        tiles = self._tiles
        mask, maskv = self.mkmasks()
        # dbg_imshow(mask)
        # print(mask.shape, maskv.shape)
        nh, nw, tilesize = tiles.shape[:3]
        # print(tilesize)
        nchannels = tiles.shape[-1]
        orig_nh = (nh // 2) + 1
        orig_nw = (nw // 2) + 1

        merge = np.zeros((orig_nh * tilesize, orig_nw * tilesize, nchannels), np.uint8)
        for j in range(nh):
            row1 = np.zeros((tilesize, orig_nw * tilesize, nchannels), np.uint8)
            row1[:, :(tilesize // 2)] = tiles[j, 0, :, :(tilesize // 2)]
            row1[:, -(tilesize // 2):] = tiles[j, -1, :, (tilesize // 2):]
            for i in range(nw - 1):
                tile0 = tiles[j, i, :, (tilesize // 2):]
                tile1 = tiles[j, i + 1, :, :(tilesize // 2)]
                blend = alphaBlend(tile0, tile1, mask)  # [:, (tilesize//4):(-tilesize//4)])
                x0 = (tilesize // 2) + (i * (tilesize // 2))
                row1[:, x0:x0 + (tilesize // 2)] = blend

            if j == 0:
                merge[:(tilesize // 2), :] = row1[:(tilesize // 2), :]
            else:
                b0 = row0[(tilesize // 2):, :]
                b1 = row1[:(tilesize // 2), :]
                blend = alphaBlend(b0, b1, maskv)  # [(tilesize//4):(-tilesize//4), :])
                y0 = j * (tilesize // 2)
                merge[y0:y0 + (tilesize // 2), :] = blend
            row0 = row1

        merge[-(tilesize // 2):, :] = row0[tilesize // 2:, :]
        origh, origw = self._orig_shape[:2]
        return cv.resize(merge, (origw, origh), interpolation=cv.INTER_LANCZOS4)


# def map_tiles(im, tilesize=128, output_size=512, interpolation=cv.INTER_AREA):
#     im_h, im_w = im.shape[:2]
#     nh = im_h // tilesize
#     nw = im_w // tilesize
#     # To get tiles with tilesize/2 overlap
#     th = (nh*2) - 1
#     tw = (nw*2) - 1
#     tiles = np.zeros((th, tw, output_size, output_size, 3), np.uint8)
#     for x in range(tw):
#         for y in range(th):
#             x0 = x * (tilesize // 2)
#             y0 = y * (tilesize // 2)
#             x1 = x0 + tilesize
#             y1 = y0 + tilesize

#             tiles[y, x] = cv.resize(im[y0:y1, x0:x1],
#                                     (output_size, output_size),
#                                     interpolation=interpolation)
#     return tiles

# def tile_even(im_, tilesize=128, output_size=256, interpolation=cv.INTER_CUBIC):
#     from math import ceil
#     h, w = im_.shape[:2]
#     nh = ceil(h / tilesize)
#     nw = ceil(w / tilesize)
#     im = cv.resize(im_, (nw * tilesize, nh * tilesize), interpolation=cv.INTER_NEAREST)
#     # To get tiles with tilesize/2 overlap
#     th = (nh*2) - 1
#     tw = (nw*2) - 1
#     tiles = np.zeros((th, tw, output_size, output_size, 3), np.uint8)
#     for x in range(tw):
#         for y in range(th):
#             x0 = x * (tilesize // 2)
#             y0 = y * (tilesize // 2)
#             x1 = x0 + tilesize
#             y1 = y0 + tilesize

#             tiles[y, x] = cv.resize(im[y0:y1, x0:x1],
#                                     (output_size, output_size),
#                                     interpolation=interpolation)
#     return tiles


from pathlib import Path

test_p = Path("stitch_test.png")
img = cv.imread(str(test_p))
# img = cv.resize(img, (3584, 1152))

stitch = Stitch(img)
# # tiles = tile_even(img)
# tiles = stitch._tiles
# mask, maskv = mkMasks(8)
# m1 = (mask * 255).astype(np.uint8)
# m1 = cv.cvtColor(m1, cv.COLOR_GRAY2BGR)
# m1 = m1.astype(np.float) / 255.0
# print(mask.shape)
# # mask = np.repeat(mask, 3, axis=2)
# # mask2 = np.broadcast_to(mask, (128,128,3))

# m2 = np.repeat(mask, 3, axis=1)
# m2.shape = (8,8,3)
# # m2 = np.reshape(m2, (8,8,3))
# print(m1)
# print(m2)
# # dbg_imshow(mask, maskv)

blend = stitch.blend()
print(img.shape, blend.shape, flush=True)
diff = cv.cvtColor(blend, cv.COLOR_BGR2GRAY) - cv.cvtColor(img, cv.COLOR_BGR2GRAY)
dbg_imshow(img, blend, diff)
# print(img.shape)
# print(tiles.shape,flush=True)
# for j in range(tiles.shape[0]):
#     for i in range(tiles.shape[1]):
#         cv.imshow("im",tiles[j, i])
#         if cv.waitKey(0) & 0xFF == ord('q'):
#             exit()


# blend = blendTiles(tiles)
# dbg_imshow(blend)
