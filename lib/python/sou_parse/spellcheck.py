import re
from pathlib import Path
from hunspell import Hunspell

from tqdm import tqdm

from perf import Perf

h = Hunspell('sv-SE', hunspell_data_dir='./hunspell')
h_en = Hunspell()


def clean_classify(path, tally):
    with open(path, 'r', encoding="utf-8") as f:
        data = f.read()

    # Just grab 5000 sentences for testing
    data = data.split("\n")  # [:10000]
    n_total = len(data)

    # Classifiers
    unclosed_parens = re.compile(r"\((?!.*?\))")
    closed_parens = re.compile(r"\((?=.*?\))")
    closed_quote = re.compile(r"""\"(?=.*?\")""")
    fullname = re.compile(r"(?<!^)(?:[A-ZÅÄÖ][a-zåäö]+\s){2,}")
    datelike = re.compile(
        r"(?:\d\d? (?:januari|februari|mars|juni|juli|augusti|september|oktober|november|december)(?:\s*\d\d\d\d)*|\d\d\d{,2}-\d\d-\d\d)")

    def is_namelike(w):
        if re.search(namelike, w):
            return True
        else:
            return False

    def is_long(line):
        # Average aloud reading speed: 183 WPM
        # Average words per max 15 sec: 46
        return len(line) > 160
        effective_words = 0
        for w in line.split(" "):
            if len(w) > 10:
                effective_words += 2
            else:
                effective_words += 1
        return effective_words >= 15

    symbols = re.compile(r"""[().,!?"':;]""")
    namelike = re.compile(r"^[A-ZÅÄÖ][a-zA-ZåäöÅÄÖ]+")

    def has_misspell(line):
        words = (" ".join(line.split("/"))).split(" ")
        for word in words:
            word = re.sub(symbols, "", word)
            if not (h.spell(word) or is_namelike(word)):
                return True
        return False

    def has_parens(line):
        if re.search(r"\(", line):
            if re.search(closed_parens, line):
                return 1
            else:
                return -1
        return 0

    def has_quote(line):
        if re.search(r"""\"""", line):
            if re.search(closed_quote, line):
                return 1
            else:
                return -1
        return 0

    def has_(pattr, line):
        return re.search(pattr, line) != None

    def classify(line):
        parens = has_parens(line)
        quote = has_quote(line)
        return [
            parens == -1 or quote == -1 or has_misspell(line),  # misspelling or unclosed parens/quote
            parens == 1,  # has parens
            quote == 1,  # has quote
            has_(fullname, line),
            has_(datelike, line),
            is_long(line)
        ]

    # perf = Perf("Spellcheck Full")
    # perf_interval = 20000

    # n_words = 0
    # n_misspelled = 0
    # for i, line in enumerate(data):
    #     words = (" ".join(line.split("/"))).split(" ")
    #     for j, word in enumerate(words):
    #         word = re.sub(symbols, "", word)
    #         if h.spell(word) or is_namelike(word):# or h_en.spell(word):
    #             n_words += 1
    #         else:
    #             # print(f"{i}:{j} {word}", flush=True)
    #             n_misspelled += 1
    #         if n_words % perf_interval == 0: perf.step(f"{perf_interval}")

    # del perf
    # print(f"Misspelled/Total: {n_misspelled} / {n_words + n_misspelled} ({n_misspelled / (n_words + n_misspelled)})")

    # perf = Perf("Classify")
    # perf_interval = 10000

    # classifications = []
    clean = []

    pbar = tqdm(data)
    for line in pbar:
        pbar.set_description(path.name)
        cls = classify(line)
        for i, val in enumerate(cls):
            if val: tally[i] += 1
        if not any(cls):
            tally[-2] += 1
            clean.append(line)
        tally[-1] += 1
        # classifications.append(cls)
        # if i % perf_interval == 0: perf.step(f"{i}")

    # del perf

    # clean = []
    # for cls in classifications:
    #     for i, val in enumerate(cls):
    #         if val: total[i] += 1
    #     if not any(cls):
    #         total[-1] += 1
    #         clean.append()

    return clean


input_d = Path("sentences")
output_d = Path("sentences_classified")
output_d.mkdir(exist_ok=True)

total = [
    0,  # spell
    0,  # paren
    0,  # quote
    0,  # name
    0,  # date
    0,  # long
    0,  # valid
    0,  # total
]

for input_p in input_d.glob("*.csv"):
    cleaned = clean_classify(input_p, total)
    output_p = output_d / input_p.name
    with open(output_p, 'w', encoding='UTF-8') as f:
        f.write("\n".join(cleaned))
# input_p = input_d / "sou_2020.csv"
# input_d = Path

n_total = total[-1]
print(f"SPELL: {total[0]} / {n_total} ({total[0] / n_total})")
print(f"PAREN: {total[1]} / {n_total} ({total[1] / n_total})")
print(f"QUOTE: {total[2]} / {n_total} ({total[2] / n_total})")
print(f"NAMES: {total[3]} / {n_total} ({total[3] / n_total})")
print(f"DATES: {total[4]} / {n_total} ({total[4] / n_total})")
print(f"LONGG: {total[5]} / {n_total} ({total[5] / n_total})")
print(f"VALID: {total[-2]} / {n_total} ({total[-1] / n_total})")
