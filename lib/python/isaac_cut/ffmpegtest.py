from pathlib import Path
import subprocess
from multiprocessing import Pool

from tqdm import trange
from subprocess import Popen, PIPE, STDOUT

XFADEFIFO = "[0:v]trim=0:{duration_minus},setpts=PTS-STARTPTS[firstclip];" \
            + "[1:v]trim=start={fade},setpts=PTS-STARTPTS[secondclip];" \
            + "[0:v]trim={duration_minus}:{duration},setpts=PTS-STARTPTS[fadeoutsrc];" \
            + "[1:v]trim=0:{fade},setpts=PTS-STARTPTS[fadeinsrc];" \
            + "[fadeinsrc]fade=t=in:st=0:d={fade}:alpha=1[fadein];" \
            + "[fadeoutsrc]fade=t=out:st=0:d={fade}:alpha=1[fadeout];" \
            + "[fadein]fifo[fadeinfifo];[fadeout]fifo[fadeoutfifo];" \
            + "[fadeoutfifo][fadeinfifo]overlay[crossfade];" \
            + "[firstclip][crossfade][secondclip]concat=n=3,format=pix_fmts=yuva444p[outputv];" \
            + "[0:a]aresample=async=1:first_pts=0,apad,atrim=0:{duration},asetpts=PTS-STARTPTS[a0];" \
            + "[1:a]aresample=async=1:first_pts=0,apad,atrim=0:{second_duration},asetpts=PTS-STARTPTS[a1];" \
            + "[a0][a1]acrossfade=d={fade}[outputa]"


# import ffmpeg

# in_file = ffmpeg.input(str(vid_p))
# (
#     ffmpeg
#     .concat(
#         in_file.trim(start_frame=342, end_frame=642),
#         in_file.trim(start_frame=642, end_frame=1004),
#         in_file.trim(start_frame=1004, end_frame=1137),
#         in_file.trim(start_frame=1314, end_frame=2361)
#     )
#     .output("trimconcat.mp4")
#     .run()
# )

def subclip(t0, t1, vfname, outname):
    vid_p = Path(vfname)
    out_p = Path(outname)

    subprocess.call([
        'ffmpeg',
        '-hwaccel', 'cuda',
        '-ss', str(t0),
        '-to', str(t1),
        '-i', str(vid_p),
        # '-ss', '1.0',
        # '-c:v', 'libx264',

        '-c:v', 'h264_nvenc',
        '-c:a', 'aac',
        # '-preset', 'fast',
        # '-preset', 'losslesshp',
        # '-rc', 'cbr_hq',
        '-b:v', '10M',
        '-maxrate:v', '20M',
        '-bufsize:v', '8M',
        # '-level:v', '4.1',
        # '-rc:v', 'vbr',
        '-threads', '1',
        # '-frames:v', str(t1),
        # '-c', 'copy',
        # '-c:v', 'copy',
        # '-c:a', 'copy',
        '{}.mp4'.format(outname)
        # '{}.mkv'.format(outname)
    ])


def AA(i):
    a = i // 26
    b = i % 26
    aa = chr(ord('A') + a) + chr(ord('A') + b)
    return aa


def compile_trims(cuts):
    """
    Get cuts as [start, end, b_fadein]
    """
    XFADE_DURATION = 2

    # basic = "[0:v]trim={}:{},format=yuva444p,fade=t=in:st=0:d={}:alpha=1,setpts=PTS-STARTPTS+{}/TB[v{}]"
    # overlay = ""
    # duration = 0
    # for i, c in enumerate(cuts):
    #     cmd = basic.format(c[0],c[1],XFADE_DURATION,duration - (XFADE_DURATION),i)
    #     duration += (c[1] - c[0]) - XFADE_DURATION

    # for i, c in enumerate(cuts):
    #     if i == 0:

    basic = "[0:v]trim={}:{},setpts=PTS-STARTPTS[v{}];" \
            + "[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a{}];"

    xfade = "[{}][{}]xfade=fade:duration=1:offset={},setpts=PTS-STARTPTS[xv{}];"
    afade = "[{}][{}]acrossfade=duration=1,asetpts=PTS-STARTPTS[xa{}];"
    # xfade = "[v{}][v{}]xfade=fade:duration={}:offset={},setpts=PTS-STARTPTS[xv{}];"\
    #       + "[a{}][a{}]acrossfade=duration={},asetpts=PTS-STARTPTS[xa{}];"

    comp = ""
    conc = ""
    for i, c in enumerate(cuts):
        cmd = basic.format(c[0], c[1], i,
                           c[0], c[1], i)

        # if cuts[]
        # if i > 0:
        #     last_duration = cuts[i-1][1] - cuts[i-1][0]
        #     ofs = last_duration - (XFADE_DURATION / 2.0)
        #     cmd2 = xfade.format(i-1, i, XFADE_DURATION, ofs, i, i-1, i, XFADE_DURATION, i)
        #     conc += "[xv{}][xa{}]".format(i,i)
        # else:
        #     conc += "[v{}][a{}]".format(i, i)
        #     cmd2 = ""
        comp += cmd
        conc += "[v{}][a{}]".format(i, i)

    duration = 0
    for i, c in enumerate(cuts):
        if i == 0:
            duration += c[1] - c[0]
            continue
        if i == 1:
            cmd = xfade.format("v0", "v1", duration - 1, i)
            cmd += afade.format("a0", "a1", i)
        elif i == len(cuts) - 1:
            cmd = "[{}][{}]xfade=fade:duration=1:offset={};".format("xv{}".format(i - 1), "v{}".format(i), duration - 1)
            cmd += "[xa{}][a{}]acrossfade=duration=1".format(i - 1, i)
        else:
            cmd = xfade.format("xv{}".format(i - 1), "v{}".format(i), duration - 1, i)
            cmd += afade.format("xa{}".format(i - 1), "a{}".format(i), i)

        duration += c[1] - c[0] - 1
        comp += cmd

    print(comp[:-1])
    return comp
    # exit()
    # for i, c in enumerate(cuts):
    #     if i == 0: continue
    #     last_duration = cuts[i-1][1] - cuts[i-1][0]
    #     ofs = last_duration - (XFADE_DURATION / 2.0)
    #     cmd = xfade.format(i-1, i, XFADE_DURATION, ofs, i, i-1, i, XFADE_DURATION, i)
    #     comp += cmd

    # conc += "concat=n={}:v=1:a=1".format(len(cuts))
    # print(comp + conc, flush=True)
    # return comp + conc


def conc_cut(videopath, cuts, outname="conc_out"):
    trimgraph = compile_trims(cuts)

    subprocess.call([
        'ffmpeg',
        '-hwaccel', 'cuda',
        '-i', str(videopath),

        '-c:v', 'h264_nvenc',
        '-c:a', 'aac',

        '-b:v', '10M',
        '-maxrate:v', '20M',
        '-bufsize:v', '8M',

        '-threads', '1',

        '-filter_complex', trimgraph,
        # '-map', "[v]",
        # '-map', "[a]",

        '{}.mp4'.format(outname)
    ])


def one_cut(c):
    # graph_v = "[0:v]trim=0:{duration};"
    graph_v = ""
    graph = graph_v + "[0:a]aresample=async=1:first_pts=0,apad,atrim=0:{duration},asetpts=PTS-STARTPTS"  # "[0:v]format=pix_fmts=yuva444p;"\

    _ = subprocess.run([
        'ffmpeg',
        '-y',  # auto overwrite
        '-hwaccel', 'cuda',

        '-ss', str(c[0]),
        '-to', str(c[1]),

        '-i', str(c[3]),

        '-c:v', 'h264_nvenc',
        '-b:v', '12M',
        '-maxrate:v', '20M',
        '-bufsize:v', '8M',
        '-c:a', 'aac',
        # '-b:a', '320k',
        '-threads', '1',

        '-filter_complex', graph.format(
            duration=c[1] - c[0]
        ),

        # '-map:v', 'outv',
        # '-map:a', 'outa',
        # '-pix_fmt', 'yuva444p',
        # '-f', 'rawvideo', # lossless is slower than encoding b/c IO

        '{}/{}_TMP.mp4'.format(str(c[4]), c[5])
    ], capture_output=True)


def ffprobe_duration(vid_p):
    try:
        # Try getting stream duration
        com = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(vid_p)
        ], capture_output=True)

        return float(com.stdout)
    except:
        try:
            # Try getting container duration instead
            com = subprocess.run([
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(vid_p)
            ], capture_output=True)

            return float(com.stdout)
        except:
            print("FFPROBE_DURATION ERR: {}".format(str(vid_p)), flush=True)
            return None


def ffprobe_duration_pipe(v):
    com = subprocess.run([
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        'pipe:'
    ], input=v, capture_output=True)


def pipe_one(c):
    graph = graph_v + "[0:a]aresample=async=1:first_pts=0,apad,atrim=0:{duration},asetpts=PTS-STARTPTS"  # "[0:v]format=pix_fmts=yuva444p;"\
    pipe = subprocess.run([
        'ffmpeg',
        '-y',  # auto overwrite
        '-hwaccel', 'cuda',

        '-ss', str(c[0]),
        '-to', str(c[1]),

        '-i', str(c[3]),

        '-c:v', 'h264_nvenc',
        '-b:v', '12M',
        '-maxrate:v', '20M',
        '-bufsize:v', '8M',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-threads', '1',

        '-filter_complex', graph.format(
            duration=c[1] - c[0]
        ),

        # '-map:v', 'outv',
        # '-map:a', 'outa',
        # '-pix_fmt', 'yuva444p',
        # '-f', 'rawvideo', # lossless is slower than encoding b/c IO
        'pipe:0'
    ], stdout=PIPE, stderr=STDOUT)
    return pipe


import tempfile


def conc_two(cuts):
    c0 = cuts[0]
    c1 = cuts[1]

    v0 = pipe_one(c0)
    v1 = pipe_one(c1)
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(v1)
        duration = ffprobe_duration_pipe(v0)
        duration1 = ffprobe_duration(fp.name)

        _ = subprocess.run([
            'ffmpeg',
            '-y',  # automatically overwrite
            '-hwaccel', 'cuda',
            '-i', 'pipe:',
            '-i', str(fp.name),
            '-c:v', 'h264_nvenc',
            '-c:a', 'aac',
            '-b:v', '10M',
            '-maxrate:v', '20M',
            '-bufsize:v', '8M',
            '-threads', '1',

            '-filter_complex', XFADEFIFO.format(
                duration_minus=duration - (fade_duration / 2.0),
                fade=fade_duration,
                duration=duration,
                second_duration=duration1
            ),

            '-map:v', '[outputv]',
            '-map:a', '[outputa]',

            str("{}{}.mp4")
        ], capture_output=True)


def mkcuts(vid_p, cuts, tmp_id="TEST"):
    vid_p = Path(vid_p)

    tmp_d = Path("./{}_TMP/".format(tmp_id))
    tmp_d.mkdir(exist_ok=True)

    for i in range(len(cuts)):
        cuts[i].append(str(vid_p))
        cuts[i].append(str(tmp_d))
        cuts[i].append(i)

    with Pool(processes=2) as pool:
        _ = pool.map(one_cut, cuts)

    # # for i in trange(len(cuts)):
    # for i, c in enumerate(cuts):
    #     # c = cuts[i]
    #     stdout = subprocess.run([
    #         'ffmpeg',
    #         '-hwaccel', 'cuda',

    #         '-ss', str(c[0]),
    #         '-to', str(c[1]),

    #         '-i', str(vid_p),

    #         '-c:v', 'h264_nvenc',
    #         '-c:a', 'aac',
    #         '-b:v', '10M',
    #         '-maxrate:v', '20M',
    #         '-bufsize:v', '8M',
    #         '-threads', '1',

    #         '{}/{}_TMP.mp4'.format(str(tmp_d), i)
    #     ], capture_output=True)


def xfade_conc(cuts, tmp_id="TEST", fade_duration=1.0):
    xfadegraph = "[0:v][1:v]xfade=fade:duration={fade}:offset={offset};[0:a][1:a]acrossfade=duration={fade}"

    xfadeoverlay = "[0:v]fade=t=out:st={}:d={}:alpha=1,setpts=PTS-STARTPTS[v0];" \
                   + "[1:v]fade=t=in:st=0:d={}:alpha=1,setpts=PTS-STARTPTS+{}/TB[v1];" \
                   + "[v0][v1]overlay[outv];[0:a][1:a]acrossfade=d={}[outa]"

    xfadefifo = "[0:v]trim=0:{duration_minus},setpts=PTS-STARTPTS[firstclip];" \
                + "[1:v]trim=start={fade},setpts=PTS-STARTPTS[secondclip];" \
                + "[0:v]trim={duration_minus}:{duration},setpts=PTS-STARTPTS[fadeoutsrc];" \
                + "[1:v]trim=0:{fade},setpts=PTS-STARTPTS[fadeinsrc];" \
                + "[fadeinsrc]fade=t=in:st=0:d={fade}:alpha=1[fadein];" \
                + "[fadeoutsrc]fade=t=out:st=0:d={fade}:alpha=1[fadeout];" \
                + "[fadein]fifo[fadeinfifo];[fadeout]fifo[fadeoutfifo];" \
                + "[fadeoutfifo][fadeinfifo]overlay[crossfade];" \
                + "[firstclip][crossfade][secondclip]concat=n=3[outputv];" \
                + "[0:a]aresample=async=1,apad,atrim=0:{duration},asetpts=PTS-STARTPTS[a0];" \
                + "[1:a]aresample=async=1,apad,atrim=0:{second_duration},asetpts=PTS-STARTPTS[a1];" \
                + "[a0][a1]acrossfade=d={fade}[outputa]"
    # + "[fadeinsrc]format=pix_fmts=yuva444p,fade=t=in:st=0:d={fade}:alpha=1[fadein];"\
    # + "[fadeoutsrc]format=pix_fmts=yuva444p,fade=t=out:st=0:d={fade}:alpha=1[fadeout];"\

    tmp_d = Path("./{}_TMP/".format(tmp_id))

    conc_p = [
        tmp_d / "conc0.mp4",
        tmp_d / "conc1.mp4"
    ]

    # duration = cuts[0][1] - cuts[0][0]

    for i in trange(len(cuts)):
        # for i, c in enumerate(cuts):
        if i == 0: continue
        c = cuts[i]
        print(i, flush=True)
        conc_in_id = (i + 1) % 2
        conc_out_id = i % 2

        cut_p0 = tmp_d / "0_TMP.mp4" if (i == 1) else conc_p[conc_in_id]
        cut_p1 = tmp_d / "{}_TMP.mp4".format(i)

        duration = ffprobe_duration(cut_p0)
        duration1 = ffprobe_duration(cut_p1)
        # print(duration, flush=True)

        _ = subprocess.run([
            'ffmpeg',
            '-y',  # automatically overwrite
            '-hwaccel', 'cuda',
            '-i', str(cut_p0),
            '-i', str(cut_p1),
            '-c:v', 'h264_nvenc',
            '-c:a', 'aac',
            '-b:v', '10M',
            '-maxrate:v', '20M',
            '-bufsize:v', '8M',
            '-threads', '1',
            # '-filter_complex', xfadeoverlay.format(
            #     duration - (fade_duration / 2.0),
            #     fade_duration,
            #     fade_duration,
            #     duration - (fade_duration / 2.0),
            #     fade_duration
            # ),
            # '-map:v', '[outv]',
            # '-map:a', '[outa]',

            '-filter_complex', xfadefifo.format(
                duration_minus=duration - (fade_duration / 2.0),
                fade=fade_duration,
                duration=duration,
                second_duration=duration1
            ),

            '-map:v', '[outputv]',
            '-map:a', '[outputa]',

            # '-filter_complex', xfadegraph.format(
            #     fade=fade_duration,
            #     offset=duration-(fade_duration/2.0)
            # ),

            str(conc_p[conc_out_id])
        ], capture_output=True)

        # duration += (c[1] - c[0]) - (fade_duration / 2.0)


if __name__ == '__main__':
    freeze_support()
