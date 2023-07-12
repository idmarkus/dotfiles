from pathlib import Path
from os import environ
from re import search
from mimetypes import guess_type

from platform import system

if system() == "Windows":
    """
    This is only because expanduser() kept
    giving me my Windows home dir on MSYS2
    """
    from os import environ


    def _expanduser(p):
        if "HOME" in environ:
            return Path(str(p).replace("~", environ["HOME"])).resolve()
        else:
            return Path(p).resolve().expanduser()
else:
    _expanduser = lambda p: Path(p).resolve().expanduser()

MIMETYPES = [
    "image",
    "video",
    "text"
]


def mimeglob(x, recurse=False):
    """
    Extended glob syntax which allows searching
    for (a few select, and guessed) mimetypes:
        *.image
        *.video
        *.text
    E.g.: mimeglob("~/**/*.text") - returns all
    'textfiles' (.html, .csv, ...), recursively
    """
    assert ("*" in x)
    f = None
    ext = search("(?<=\*)\.(\w+)", x)
    if ext and ext[1] in MIMETYPES:
        x = x[:ext.span()[0]]
        f = lambda y: str(guess_type(y)[0]).split("/")[0] == ext[1]

    r = search(r"\*", x).span()[0]
    root = _expanduser(x[:r])
    expr = x[r:]

    if recurse:
        if f:
            return [p for p in root.rglob(expr) if f(p)]
        else:
            return [p for p in root.rglob(expr)]
    else:
        if f:
            return [p for p in root.glob(expr) if f(p)]
        else:
            return [p for p in root.glob(expr)]


def mimerglob(x):
    return mimeglob(x, recurse=True)
