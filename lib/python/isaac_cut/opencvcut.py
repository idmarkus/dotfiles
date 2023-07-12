import cv2 as cv
import numpy as np
from pathlib import Path
import subprocess
from subprocess import PIPE, STDOUT

from tqdm import tqdm, trange


def ffprobe_duration_audio(vid_p):
    try:
        com = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(vid_p)
        ], capture_output=True)

        return float(com.stdout)
    except:
        print("FFPROBE_DURATION ERR: {}".format(str(vid_p)))
        exit()


def cutaudio(cuts, vid_p, fade_duration=1.0, tmp_id="TEST", fps=60):
    tmp_d = Path("./{}_TMP/".format(tmp_id))
    tmp_d.mkdir(exist_ok=True)

    graph = "[0:a]aresample=async=1:first_pts=0,apad,atrim=0:{duration},asetpts=PTS-STARTPTS"

    # Make tmp cut clips
    for i, c in enumerate(cuts):
        out_p = tmp_d / "{}.wav".format(i)
        _ = subprocess.run([
            'ffmpeg',
            '-y',  # auto overwrite
            '-hwaccel', 'cuda',

            '-ss', str(c[0]),
            '-to', str(c[1]),

            '-i', str(vid_p),

            '-filter_complex', graph.format(duration=c[1] - c[0]),
            '-map', 'a',
            str(out_p)
        ], capture_output=False)

    conc_base = "[0:a]aresample=async=1,apad,atrim=0:{duration},asetpts=PTS-STARTPTS[a0];" \
                + "[1:a]aresample=async=1,apad,atrim=0:{second_duration},asetpts=PTS-STARTPTS[a1];"
    conc_fade = "[a0][a1]acrossfade=d={fade}"
    conc_conc = "[a0][a1]concat=n=2:v=0:a=1"

    conc_p = [
        tmp_d / "conc0.wav",
        tmp_d / "conc1.wav"
    ]

    conc_out_id = 0

    # duration = 0
    for i, c in enumerate(cuts):
        # f0 = round(c[0] * fps)
        # f1 = round(c[1] * fps)
        # c0 = float(f0) / fps
        # c1 = float(f1) / fps

        if i == 0:
            # duration = c1 - c0
            continue

        conc_in_id = (i + 1) % 2
        conc_out_id = i % 2

        cut_p0 = tmp_d / "0.wav" if (i == 1) else conc_p[conc_in_id]
        cut_p1 = tmp_d / "{}.wav".format(i)

        out_p = conc_p[conc_out_id] if i < len(cuts) - 1 else tmp_d / "SND_TMP.wav"

        print(out_p, flush=True)
        duration = ffprobe_duration_audio(cut_p0)
        duration1 = ffprobe_duration_audio(cut_p1)
        # duration1 = c1 - c0
        should_fade = c[2]  # fadein True/False

        filtergraph = conc_base.format(duration=duration, second_duration=duration1)
        filtergraph += conc_fade.format(fade=fade_duration) if should_fade else conc_conc

        # duration += duration1
        _ = subprocess.run([
            'ffmpeg',
            '-y',  # automatically overwrite
            '-hwaccel', 'cuda',
            '-i', str(cut_p0),
            '-i', str(cut_p1),

            '-filter_complex', filtergraph,

            '-map', 'a',

            str(out_p)
        ], capture_output=False)  # stdout=PIPE, stderr=STDOUT)

    if len(cuts) == 1:
        p = tmp_d / "0.wav"
        np = tmp_d / "SND_TMP.wav"
        p.rename(np)
    # Remove tempfiles
    for i in range(len(cuts)):
        p = tmp_d / "{}.wav".format(i)
        if p.exists(): p.unlink()

    for p in conc_p:
        if p.exists(): p.unlink()


def muxfile(tmp_id="TEST"):
    audio_p = Path("./{}_TMP/SND_TMP.wav".format(tmp_id))
    video_p = Path("./{}_TMP/VID_TMP.avi".format(tmp_id))

    out_p = Path("./{}_TMP/output.mp4".format(tmp_id))
    _ = subprocess.run([
        'ffmpeg',
        '-y',
        '-i', str(video_p),
        '-i', str(audio_p),
        # '-filter_complex',
        # "[1:a]aresample=async=1:first_pts=0,apad",
        '-c:v', 'copy',
        '-c:a', 'aac',
        str(out_p)
    ], capture_output=False)  # stdout=PIPE, stderr=STDOUT)


def cvcut(cuts, vid_p, fade_duration=1.0, tmp_id="TEST", total_frames=0):
    # Setup tmp dir
    out_d = Path("./{}_TMP/".format(tmp_id))
    out_d.mkdir(exist_ok=True)
    out_p = out_d / "VID_TMP.avi"

    # Grab input video and info
    cap = cv.VideoCapture(str(vid_p))
    fps = cap.get(cv.CAP_PROP_FPS)
    dim = (int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))

    # Find even frame length of fade
    fade_half = round(fade_duration * fps) // 2
    fade_frames = fade_half * 2

    if out_p.exists():
        cutaudio(cuts, vid_p, fade_duration=float(fade_half) / float(fps), tmp_id=tmp_id)
        muxfile(tmp_id=tmp_id)

        tmpvid_p = out_d / "VID_TMP.avi"
        tmpsnd_p = out_d / "SND_TMP.wav"

        if tmpvid_p.exists(): tmpvid_p.unlink()
        if tmpsnd_p.exists(): tmpsnd_p.unlink()

        return

    # Setup output video stream
    out = cv.VideoWriter(str(out_p), cv.VideoWriter_fourcc(*'XVID'), fps, dim)

    framecount = 0

    transition_in = []
    transition_out = []

    def write_frame(frame):
        out.write(frame)

    # rebase = []

    for I in trange(len(cuts)):
        c = cuts[I]
        # for I, c in enumerate(cuts):
        f0 = round(c[0] * fps)
        f1 = round(c[1] * fps)
        should_fadein = c[2]
        should_fadeout = c[3]

        ret = cap.isOpened()

        # Seek by frames before
        while ret and (framecount < f0 or framecount == 0):
            ret, frame = cap.read()
            framecount += 1

        # First actual frame

        # Add fadein frames
        if (not should_fadein) and len(transition_out):
            for f in transition_out:
                write_frame(f)
            transition_out = []

        while ret and framecount < (f0 + fade_half):
            transition_in.append(frame)
            ret, frame = cap.read()
            framecount += 1

        # Construct transition
        if len(transition_out) and should_fadein:
            print("t_out {}, t_in {}".format(len(transition_out), len(transition_in)), flush=True)
            for i, f_out in enumerate(transition_out):
                try:
                    f_in = transition_in[i]
                except:
                    print("\ni > transition_in: i: {}".format(i), flush=True)
                    print("\nshould_fadein {}, should_fadeout {}, transition_in {}, transition_out {}".format(
                        should_fadein, should_fadeout, len(transition_in), len(transition_out)), flush=True)
                    print("last_should_fadeout {}".format(cuts[I - 1][3]))
                    break
                a_in = i / float(fade_half)
                a_out = 1.0 - a_in
                lerp = cv.addWeighted(f_out, a_out, f_in, a_in, 0.0)
                write_frame(lerp)
            transition_in = []
            transition_out = []

            # if I > 0:
            #     rebase[I-1]["end"] = out_framecount
            #     rebase[I-1]["fadeout"] = fade_half
        else:
            for f in transition_in:
                write_frame(f)
            transition_in = []
            # rebase[-1]["fadein"] = 0

        # Add proper frames
        if (not f1):  # or I+1 == len(cuts):
            while ret and cap.isOpened():
                write_frame(frame)
                ret, frame = cap.read()
                framecount += 1
            cuts[I][1] = float(framecount) / float(fps)

        elif should_fadeout:
            while ret and framecount < (f1 - fade_half):
                write_frame(frame)
                ret, frame = cap.read()
                framecount += 1
            # Add transition out frames
            while ret and framecount < f1:
                transition_out.append(frame)
                ret, frame = cap.read()
                framecount += 1
        else:
            while ret and framecount < f1:
                write_frame(frame)
                ret, frame = cap.read()
                framecount += 1

        if not ret:
            print("NOT ret FOR I: {}".format(I), flush=True)

    # Add rest frames
    for f in transition_out:
        write_frame(f)

    cap.release()
    out.release()

    cutaudio(cuts, vid_p, fade_duration=float(fade_half) / float(fps), tmp_id=tmp_id)
    muxfile(tmp_id=tmp_id)

    tmpvid_p = out_d / "VID_TMP.avi"
    tmpsnd_p = out_d / "SND_TMP.wav"

    if tmpvid_p.exists(): tmpvid_p.unlink()
    if tmpsnd_p.exists(): tmpsnd_p.unlink()
