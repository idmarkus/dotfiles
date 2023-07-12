from multiprocessing import Pool
import re
from pathlib import Path

from perf import Perf

dot_pattern = re.compile(r"\.")


def split_file(input_path, chunksize=10000000):
    perf = Perf(str(input_path))
    with open(input_path, "r", encoding="utf-8") as f:
        data = f.read()
    perf.step(f"{input_path} Read")

    fname_pattern = "splits/" + input_path.name[:-4] + "_{}.csv"
    start = 0
    i = 0
    while (start + chunksize) < len(data):
        end = start + chunksize
        # match = re.search(dot_pattern, data[end:end+100])
        # if match: end = match.span()[1]
        split = data[start:end]
        with open(fname_pattern.format(i), "w+", encoding="utf-8") as f:
            f.write(split)
        perf.step(f"{input_path} {i}")
        start = end
        i += 1
    if start < len(data):
        split = data[start:]
        with open(fname_pattern.format(i), "w+", encoding="utf-8") as f:
            f.write(split)
        perf.step(f"{input_path} {i}")
    del perf
    return True


def split_files(inputs, n_workers=8):
    output_d = Path("splits")
    output_d.mkdir(exist_ok=True)

    # paths = [(inp, output_d / inp.name) for inp in inputs]
    paths = list(inputs)
    perf = Perf("Splits")
    with Pool(processes=n_workers) as pool:
        for i, res in enumerate(pool.imap_unordered(split_file, paths)):
            continue
            # perf.step(f"{i}")
    del perf


if __name__ == "__main__":
    input_d = Path("cleaned")
    inputs = input_d.glob("*.csv")

    split_files(inputs)
