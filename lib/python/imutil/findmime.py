import mimetypes
from pathlib import Path


def isImageMimetype(fname):
    from mimetypes import guess_type
    if isinstance(fname, Path): fname = fname.name
    guess = guess_type(fname)
    return guess is not None and guess[0] is not None and guess[0][:5] == "image"


def findImagesRecursive(path):
    if isinstance(path, str): path = Path(path)
    return [str(p) for p in path.rglob("*") if isImageMimetype(p.name)]
