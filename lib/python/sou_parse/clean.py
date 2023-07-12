from multiprocessing import Pool
import re
from pathlib import Path

from abbreviations import subs_abbrev
from perf import Perf

subs_collapse = [(re.compile(x[0], re.IGNORECASE), x[1]) for x in [
    # Pagination
    (r"(?:\s{2,}(?:\d+\s+(?:.+\n+){,2}|SOU.\d+:\s*\d+)\s*)", r" "),
    # Collapse whitespace
    (r"\s+", r" "),
    # Date spans e.g. januari-februari, 2020-2022
    # (r"(?<=januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december|\d\d\d\d)-\s+", "-"),
    # Remove hyphenation
    # (r"(\w{2,})\-\s(?!och)(\w{2,})", r"\1\2"),
    (r"(?<=[A-Za-zåäöÅÄÖ])- (?!och)(?=\w)", "")
]]

subs_unicode = [(re.compile(x[0]), x[1]) for x in [
    # Replace unicode
    (r"£", r"GBP"),
    (r"—|–|−|­", r"-"),
    (r"»|”|«", r'"'),
    (r"€", r"EURO"),
    (r"§", r""),
    (r"½", r"1/2"),
    (r" | ", r"_"),
    (r"æ", r"ae"),
    (r"´|‘|’", r"'"),
    (r"…", r"..."),
    (r"•", r"><>"),
    (r"×", r"*"),
    (r"±", r"+-")
]]


def replace(subs, text):
    for exp, rep in subs:
        text = re.sub(exp, rep, text)
    return text


def clean_worker(paths):
    perf = Perf(paths[0])
    with open(paths[0], "r", encoding="utf-8") as f:
        text = f.read()
    perf.step(f"{paths[0]} : Read")

    text = replace(subs_collapse, text)
    perf.step(f"{paths[0]} : Collapse")
    text = replace(subs_abbrev, text)
    perf.step(f"{paths[0]} : Abbrev")
    text = replace(subs_unicode, text)
    perf.step(f"{paths[0]} : Unicode")

    with open(paths[1], "w+", encoding="utf-8") as f:
        f.write(text)
    perf.step(f"{paths[0]} : Write")
    del perf
    return True


def clean(inputs, n_workers=8):
    output_d = Path("cleaned")
    output_d.mkdir(exist_ok=True)

    paths = [(inp, output_d / inp.name) for inp in inputs]
    perf = Perf("Cleanpool")
    with Pool(processes=n_workers) as pool:
        for i, res in enumerate(pool.imap_unordered(clean_worker, paths)):
            continue
            # perf.step(f"{i}")
    del perf
