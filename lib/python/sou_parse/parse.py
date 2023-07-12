from pathlib import Path
import csv
import re
from unidecode import unidecode
from cleanups import replace_abbrevs, clean_undefined_abbrevs
import tqdm

from perf import Perf

sentence_pattern = re.compile(
    r"""(?<=\.\s)[A-ZÅÄÖ][a-zåäö]*(?:[\s\-]+['"(>]*(?:[A-ZÅÄÖa-zåäö][a-zåäö\/]*|[A-ZÅÄÖ]{2,5}(?::s)*|\d+(?:[.,:]\d+)*%*|-+)['")>]*[:;,]*){2,}[.?!](?=\s)""")


def replace_unicode(text):
    subs = [(re.compile(x[0]), x[1]) for x in [
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

    for exp, rep in subs:
        text = re.sub(exp, rep, text)

    return text


from number import spell_ordinal, spell_year


def expand_dates(text):
    pattern = re.compile(
        r"(?<=den )(\d\d{,1})( (?:januari|jan|februari|feb|mars|april|maj|juni|jun|juli|jul|augusti|aug|september|sept|oktober|okt|november|nov|december|dec) )(\d\d\d\d)",
        re.IGNORECASE)

    def datesub(match):
        return spell_ordinal(match.group(1)) + match.group(2) + spell_year(match.group(3))

    return re.sub(pattern, datesub, text)


def clean_raw(text, perf=None):
    # Remove pagination
    text = re.sub(r"(?:\s{2,}(?:\d+\s+(?:.+\n+){,2}|SOU.\d+:\s*\d+)\s*)", r" ", text)
    if perf: perf.step("pagination")

    # Collapse whitespace
    # text = re.sub(r"\s{2,}", r" ", text)
    text = re.sub(r"\s+", r" ", text)
    if perf: perf.step("whitespace")

    # Remove hyphenation
    text = re.sub(r"(\w{2,})\-\s(?!och)(\w{2,})", r"\1\2", text)
    if perf: perf.step("dehyphenate")

    text = replace_abbrevs(text)
    if perf: perf.step("debreviate")

    text = clean_undefined_abbrevs(text)
    if perf: perf.step("undef. abbr.")

    # # ÅÄÖåäö
    # sub = {
    #     r"å": r"@aaa",
    #     r"Å": r"@AAA",
    #     r"ä": r"@aeae",
    #     r"Ä": r"@AEAE",
    #     r"ö": r"@oeoe",
    #     r"Ö": r"@OEOE"
    # }
    # for k, v in sub.items():
    #     text = re.sub(k, v, text)

    # if perf: perf.step("dedotify")

    # # unidecode
    # text = unidecode(text)
    # if perf: perf.step("unidecode")

    # # redotify
    # for k, v in sub.items():
    #     text = re.sub(v, k, text)
    # if perf: perf.step("redotify")

    text = replace_unicode(text)
    if perf: perf.step("de-unicode")

    # text = expand_dates(text)
    # if perf: perf.step("dates")
    # decodefix = {
    #     r">>": r"\"",
    #     r"--": r"-"
    # }

    return text


input_d = Path("./sou_dataset/dataset")
inputs = list(input_d.glob("*.csv"))

clean_d = Path("cleaned")
clean_d.mkdir(exist_ok=True)

cleaned = list(clean_d.glob("*.csv"))
if any([f"cleaned_{x.name}" not in [y.name for y in cleaned] for x in inputs]):
    print("\nCLEANING INPUTS\n", flush=True)
    perf = Perf("clean")
    for input_p in inputs:
        clean_p = clean_d / f"cleaned_{input_p.name}"
        if clean_p.exists(): continue
        perf2 = Perf(input_p.name)
        with open(input_p, 'r', encoding="utf-8") as f:
            data = clean_raw(f.read(), perf=perf2)
            with open(clean_p, "w+", encoding="utf-8") as f2:
                f2.write(data)
        del perf2
    del perf
    # exit()

output_d = Path("sentences")
output_d.mkdir(exist_ok=True)

print("\nSENTENIZING CLEANED\n", flush=True)

inputs = clean_d.glob("*.csv")

from timeout import timeout


# def safenext(iterator):
#     with time_limit(1, "iter"):
#         return iterator.__next__()

@timeout(0.01)
def safenext(iterator):
    return iterator.__next__()


for input_p in inputs:
    fname = input_p.name[:-4]
    if fname == "cleaned_sou_1922-1929": continue
    # if fname == "cleaned_sou_1930-1939": continue
    # if fname == "cleaned_sou_1940-1949": continue

    output_p = output_d / f"{fname}_sentences.txt"
    # perf = Perf(fname)
    with open(input_p, 'r', encoding="utf-8") as f:
        perf = Perf("Read {}".format(input_p))
        data = f.read()
        del perf

    print(len(data), flush=True)
    bloclen = 500000
    blocs = len(data) // bloclen
    output = []
    tenkout = u""
    n_match = 0
    perf = Perf("sentences")

    for i in range(blocs - 1):
        for match in re.finditer(sentence_pattern, data[i * bloclen:(i + 1) * bloclen]):
            # tenkout += match.group() + "\n"
            output.append(match.group())
            # output.append(data[(i*bloclen) + match.span()[0]:(i*bloclen) + match.span()[1]])
            # nblocmatch += 1
            n_match += 1
            # if n_match % 10000 == 0:
            # output.append(tenkout)
            # tenkout = ""
            # perf.step(f"{i} : {n_match}")
        # n_match += nblocmatch
        perf.step(f"{i},{n_match}")
    del perf
