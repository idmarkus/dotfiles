import re
from pathlib import Path

input_d = Path("cleaned")
inputs = input_d.glob("*.csv")

# input_p = input_d / "cleaned_test_2020.csv"


pattern = r"(?<=\s)(?:(?:[a-zåäö]{1,3}\.\s{,1}){1,3}|[a-zåäö]{2,}[bcdfghjklmnpqrstvwxz]\.)(?=\s)"
pattern = r"(?<=\s)(?:(?:[a-zåäö]{1,3}\.\s{,1}){1,3}|[a-zåäö]{2,}[bcdfghjklmnpqrstvwxz]{2,}\.)(?=\s)"
pattern = r"(?<=\s)(?:(?:[a-zåäö]{1,3}\.\s{,1}){2,3})(?=\s)"
abbrev_pattern = re.compile(pattern, re.IGNORECASE)
from cleanups import _abbrev, abbreviations

count = {}

for input_p in inputs:
    with open(input_p, "r", encoding="utf-8") as f:
        data = f.read()

        for i, match in enumerate(re.finditer(abbrev_pattern, data)):
            # if i > 100: break
            group = match.group()
            if group not in count:
                count[group] = 1
            else:
                count[group] += 1
for k, v in sorted(count.items(), key=lambda kv: kv[1]):
    print(k, v)

total = sum(kv[1] for kv in count.items())
print("total:", total)

newabbrevs = """
t.ex., till exempel
m.fl., med flera
bl.a., bland annat
m.m., med mera
s.k., så kallat
d.v.s., det vill säga
t.o.m., till och med
fr.o.m., från och med
p.g.a., på grund av
f.n., för närvarande
o.s.v., och så vidare
o.dyl., och dylikt
i.e., det vill säga
e.g., till exempel
fil.dr., filosofie doktor
fil.kand., fil kand
kap., kapitel
m.a.o., med andra ord
f.d., före detta
fig., figure
tab., tabell
forts., fortsättning
ibid.|ib., ibid
i.o.m., i och med
k:a, kyrka
n:o, nummer
nästk., nästkommande
omkr., omkring
op., opus
ordf., ordöfrande
prof., professor
resp., respektive
ref., referens
s.|sid., sida
s.a.s., så att säga
tfn|tel., telefon
u.f.a., under förutsättning att
e.kr.|a.d., efter kristus
kungl. maj:t, kungliga majestät
ang., angående
"""
# for i, x in enumerate(_abbrev):
#     # matches = re.findall(x[0], data)
#     # print(abbreviations.split("\n")[i+1].split(",")[0], flush=True)
#     for match in re.finditer(x[0], data):
#         print(match.group(), match.span())
# if len(matches) > 0:
# print(matches[0])
# print(abbreviations.split("\n")[i+1].split(",")[0], len(matches), flush=True)
