def ms_to_frame(t, fps=60):
    frame = (float(t) / 1000.0) * fps
    return round(frame)


def frame_to_sec(t, fps=60):
    return float(t) / float(fps)


def frame_to_ms(t, fps=60):
    return frame_to_sec(t, fps=fps) * 1000


def ms_to_sec(t, fps=60):
    frame = ms_to_frame(t, fps=fps)
    return frame_to_sec(frame, fps=fps)
    # return float(t) / 1000.0


def sec_to_frame(t, fps=60):
    return ms_to_frame(t * 1000)
