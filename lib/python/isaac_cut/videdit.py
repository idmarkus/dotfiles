from pathlib import Path

# class VideoClip():
#     def __init__(self, vid_p):
#         self.vid_p = Path(vid_p)
#         assert(vid_p.exists())

# class Cut():
#     def __init__(self, t0, t1=None, fadein=None, fadeout=None):
#         self.t0 = t0
#         self.t1 = t1
#         self.fadein = None
#         self.fadeout = None

#     def crossfade(self, t=1.0):
#         self.fadein

# class VidEdit():

#     def __init__(self, videofile):
#         self.vid_p = Path(videofile)
#         self.cuts  = []

#     def cut(self, t0, t1=None):

"""
vid0 = VideoClip("video0.mp4")
vid1 = Clip("video1.mp4")

edit = Editor()
edit.render([
    vid0[0 : 20.0],
    vid1[5.33 : ].crossfade()
])
"""


class TestSlice():
    def __init__(self):
        self.nothing = None

    def __getitem__(self, key):
        if isinstance(key, slice):
            print(key.start, key.stop, key.step)


# class Video():
#     def __init__(self, vid_p)

# test = TestSlice()
# test[2 : 5 : 3]
# test[2 : ]
# test[: -1 : 2]
# test["a" : 5]

vid = Video("video.mp4")

vid.clip(0, 5)
vid.clip(10, 20)

edit([
    vid[0: 5],
    vid[10: 20]
])
