from pathlib import Path
import re

input_p = Path("cleaned/sou_1970-1979.csv")

with open(input_p, "r", encoding="utf-8") as f:
    data = f.read()

# start = 62000000
start = 107000000
start = 125500000
print(len(data), len(data) > start)
# start = 497500000
# start = 10000000

data = data[start:start + 500000]

sentence_pattern = re.compile(
    r"""(?<=\.\s)[A-ZÅÄÖ][a-zåäö]*(?:[\s\-]+['"(]*(?:[A-ZÅÄÖa-zåäö][a-zåäö\/]*|[A-ZÅÄÖ]{2,5}(?::s)*|\d+(?:[.,:]\d+)*%*|-+)['")]*[:;,]*){2,}[.?!](?=\s)""")

import time

t = time.perf_counter_ns()

out = []
for i, match in enumerate(re.finditer(sentence_pattern, data)):
    out.append(match.group())
    # print(i, match.span(), flush=True)

dt = "{:07}".format(time.perf_counter_ns() - t)

print(len(out), "{}.{}ms".format(dt[:-6], dt[-6:]))
