from pathlib import Path

from itertools import chain
from collections.abc import Iterable
from mimetypes import guess_type

from mimeglob import mimeglob, _expanduser


class Inputs(Iterable):
    """
    Create an iterable of file Paths from any pathlikes.

    Supports arguments as single(s) or Iterable(s) in any constellation:
     + String paths - and regular Globs:  '~/data'        '**/*.csv'
     + An extended MIMETYPE Glob syntax:  '*.text'        '**/*.image'
     + Premade/generators pathlib Paths:  Path('file.o')  Path('.').iterdir()

    >> paths = Inputs(["../**/*.image", "../res"], "/data/file.dat")

    Returns an iterator of absolute pathlib Path():s to files.
    For a list of strings, use [str(p) for p in inputs]    

      NOTE: All paths are userexpanded (!)

    >> for p in paths:
    >>     print(p)

    Will print, without duplicates, in preserved order of arguments:
     + All filepaths in '../**/* (recursive) with MIMETYPE 'image' (jpg, png, ...)
     + All filepaths found under (non-recursive) the directory '../res'
     + The filepath '/data/file.dat'

    If no valid files are found, paths is equivalent to an empty list []
    """

    def __ff(self, x):
        """
        Recursively disambiguate input arguments.

        Note: The returned chain must be unlazied -- list(__ff(x)),
        otherwise, by default, elements are consumed on iteration
        """
        flatmap = lambda func, *iterable: chain.from_iterable(map(func, *iterable))

        if isinstance(x, str):
            if '*' in x:
                return flatmap(self.__ff, mimeglob(x))
            else:
                x = Path(x)

        if isinstance(x, Path):
            if not x.exists(): return []

            if x.is_dir():
                # We don't want to manually recurse here since we support globs
                return flatmap(self.__ff, (y for y in x.iterdir() if y.is_file()))
            elif x.is_file():
                # Recursion end-point
                return [_expanduser(x)]

        elif isinstance(x, Iterable):
            return flatmap(self.__ff, x)

        return []  # Fall-through

    def __init__(self, *args, unique=True):
        if unique:
            self.paths = list(set(self.__ff([*args])))
        else:
            self.paths = list(self.__ff([*args]))

    def __next__(self):
        return self.paths.__next__()

    def __iter__(self):
        return self.paths.__iter__()

    def __len__(self):
        return len(self.paths)


if __name__ == "__main__":
    tests = (
        "../../dotfiles/**/*.text",
    )

    inp = Inputs(*tests)
    for i in inp:
        print(i)

    for i in inp:
        print(i)
    print(len(inp))
    # for t in tests:
    # paths = mimeglob(t)
    # print(len(paths))
    # print(mimeglob(t), flush=True)
