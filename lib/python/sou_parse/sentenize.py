import re
import time
import multiprocessing
from pathlib import Path
from multiprocessing import Pool, TimeoutError
from perf import Perf

sentence_pattern = re.compile(
    r"""(?<=\.\s)[A-ZÅÄÖ][a-zåäö]*(?:[\s\-]+['"(]*(?:[A-ZÅÄÖa-zåäö][a-zåäö\/]*|[A-ZÅÄÖ]{2,5}(?::s)*|\d+(?:[.,:]\d+)*%*)['")]*[:;,]*){3,}[.?!](?=\s)""")


def blocsearch(bloc):
    output = []
    search = re.finditer(sentence_pattern, bloc)
    for match in search:
        output.append(match.group())
    return output


def sentenize_file(path):
    out_p = Path(f"sentences/{path.name}")
    if out_p.exists(): return True
    print("START", path, flush=True)
    perf = Perf(str(path))
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    # output = "\n".join(re.findall(sentence_pattern, data))
    output = []
    for i, match in enumerate(re.finditer(sentence_pattern, data)):
        output.append(match.group())
        if i % 100000 == 0: perf.step(f"{path} {i}")
    output = "\n".join(output)
    with open(out_p, "w+", encoding="utf-8") as f:
        f.write(output)
    del perf
    del data
    del output
    del out_p
    return True


def sentenize_files(inputs, n_workers=8):
    output_d = Path("sentences")
    output_d.mkdir(exist_ok=True)

    # paths = [(inp, output_d / inp.name) for inp in inputs]
    paths = list(inputs)
    perf = Perf("Sentenize")
    n_batch = len(paths) // n_workers
    with Pool(processes=n_workers) as pool:
        # for batch in range(n_batch):
        #     start = batch * n_workers
        #     end = n_workers if start + n_workers < len(paths) else (len(paths) - start)
        #     res = [pool.apply_async(sentenize_file, (paths[start + i],)) for i in range(end)]
        #     for i, r in enumerate(res):
        #         try:
        #             _ = r.get()
        #         except TimeoutError:
        #             print(f"TimeoutError for file {paths[start + i]}")
        # continue
        for i, res in enumerate(pool.imap_unordered(sentenize_file, paths)):
            continue
            # perf.step(f"{i}")
    del perf


def sentenize(data, n_workers=8, bloc_size=1000000, timeout=0.3):
    n_blocs = len(data) // bloc_size
    n_batch = n_blocs // n_workers
    output = []
    with Pool(processes=n_workers) as pool:
        # chunks = [str(data[i*bloc_size:(i+1)*bloc_size]) for i in range(n_blocs - 1)]
        # it = pool.imap_unordered(blocsearch, data, bloc_size)
        # for i in it:
        # output += i
        # n_timeouts = 0
        # while True:
        #     try:
        #         batch = it.next(timeout)
        #         output += batch
        #     except Exception as e:
        #         if isinstance(e, StopIteration):
        #             break
        #         elif isinstance(e, TimeoutError):
        #             n_timeouts += 1
        #             if n_timeouts % 10 == 0: print("TimeoutError", flush=True)
        #         else:
        #             raise e

        # print(f"N Timeouts: {n_timeouts}")

        for batch in range(n_batch):
            start = (batch * n_workers) * bloc_size
            assert (start < len(data))
            datas = list([str(data[start + (i * bloc_size): start + ((i + 1) * bloc_size)]) for i in range(n_workers)])
            res = [pool.apply_async(blocsearch, (datas[i],)) for i in range(n_workers)]
            for i, r in enumerate(res):
                try:
                    output += r.get(timeout=timeout)
                except TimeoutError:
                    print("TimeoutError at {}".format(start + (i * bloc_size)), flush=True)
                    continue

    return output


if __name__ == "__main__":
    input_d = Path("cleaned")
    inputs = input_d.glob("*.csv")
    sentenize_files(inputs)
