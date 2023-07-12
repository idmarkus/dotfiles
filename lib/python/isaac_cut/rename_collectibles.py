from pathlib import Path
import cv2 as cv
import numpy as np
# col_d = Path("resources/collectibles")
from spriteedit import scale, overlay_a


# iids = []

# for p in col_d.iterdir():
#     iid = p.stem[:3]
#     if iid.isnumeric():
#         iids.append(int(iid))
#     # if iid.isnumeric():
#     #     new_p = p.parent / f"{p.stem[13:16]}{p.suffix}"
#     #     p.rename(new_p)


# for i in range(733):
#     if not i in iids:
#         print(i)

# p = Path("resources/levelitem_001_itemaltar.png")
# im = cv.imread(str(p), cv.IMREAD_UNCHANGED)

# altar = im[:32, :32]
# out_p = Path('resources/altar.png')
# cv.imwrite(str(out_p), altar)


def cut_backdrops():
    d = Path("resources/backdrop")
    out_d = d / Path("edited")
    out_d.mkdir(exist_ok=True)

    for p in d.iterdir():
        if p.stem[-6:] == "nfloor":
            floorname = p.stem.split("_")[1]
            im = cv.imread(str(p), cv.IMREAD_UNCHANGED)
            cut = im[:182, :130]
            # cut = im[2:182,2:128]
            # cut = im[4:182, 4:126]
            h, w = cut.shape[:2]
            print(w, h, flush=True)
            # flip = cv.flip(cut[h//2, ])
            flip_len = 32
            cut[-flip_len:, :] = cv.flip(cut[:flip_len, :], -1)
            # cut = scale(cut, 5)
            out_p = out_d / f"{floorname}.png"
            cv.imwrite(str(out_p), cut)
            # cv.imshow("im", cut)
            # if cv.waitKey(0) & 0xFF == ord('q'):
            # break

    cv.destroyAllWindows()


def comp_planetarium():
    d = Path("resources/backdrop")

    back_p = d / "planetarium_blue_base.png"
    mid_p = d / "planetarium.png"
    over_p = d / "planetarium_overlay.png"

    print(mid_p.exists())
    bg = cv.imread(str(back_p))  # , cv.IMREAD_UNCHANGED)
    mid = cv.imread(str(mid_p), cv.IMREAD_UNCHANGED)
    over = cv.imread(str(over_p), cv.IMREAD_UNCHANGED)

    # trim_t = 52
    # trim_b = 39
    # trim_w = 51
    trim_t = 70
    trim_b = 55
    trim_w = 55
    mid = mid[trim_t:-trim_b, trim_w:-trim_w]
    bg = bg[trim_t:-trim_b, trim_w:-trim_w]
    mid_h, mid_w = mid.shape[:2]
    over = cv.resize(over, (mid_w, mid_h), interpolation=cv.INTER_NEAREST)
    bg = cv.resize(bg, (mid_w, mid_h))
    out_d = Path("resources/backdrop/scaled")
    out_d.mkdir(exist_ok=True)
    out_bg = out_d / "starmap.png"
    cv.imwrite(str(out_bg), cv.resize(bg, (1280, 720), interpolation=cv.INTER_NEAREST))
    # bg = np.ones((mid_h,mid_w,3), np.uint8) * 235
    over[:, :, :3] = 255 - over[:, :, :3]
    over[:, :, 3] = over[:, :, 3] * 0.7
    # mid[:,:,3] = mid[:,:,3] * 1.2
    overlay_a(bg, mid, 0, 0)
    # overlay_a(bg, over, 0, 0)
    # bg = scale(bg, 4)
    bg = cv.resize(bg, (1280, 720), interpolation=cv.INTER_NEAREST)
    over = cv.resize(over, (1280, 720), interpolation=cv.INTER_NEAREST)

    out_p = out_d / "planetarium.png"
    cv.imwrite(str(out_p), bg)
    out_over = out_d / "overlay.png"
    cv.imwrite(str(out_over), over)

    # bg = scale(bg, 0.5)
    cv.imshow("im", bg)
    if cv.waitKey(0):
        cv.destroyAllWindows()
        return
    back = cv.resize(back, (1280, 720), interpolation=cv.INTER_NEAREST)
    back = cv.resize(back, (1280, 720), interpolation=cv.INTER_NEAREST)
    back = cv.resize(back, (1280, 720), interpolation=cv.INTER_NEAREST)


def rescale_backdrops():
    d = Path("resources/backdrop/edited")
    out_d = Path("resources/backdrop/scaled")
    out_d.mkdir(exist_ok=True)

    for p in d.iterdir():
        name = p.stem
        ext = p.suffix
        im = cv.imread(str(p), cv.IMREAD_UNCHANGED)
        crop = 2
        im = im[crop:-crop, crop:-crop]
        im = cv.rotate(im, cv.ROTATE_90_CLOCKWISE)
        im = cv.resize(im, (1280, 720), interpolation=cv.INTER_NEAREST)
        out_p = out_d / f"{name}{ext}"
        cv.imwrite(str(out_p), im)
        print(ext)


# comp_planetarium()
rescale_backdrops()
