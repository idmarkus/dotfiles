import re

abbreviations = [tuple(line.split(", ")) for line in """
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
n:o|nr, nummer
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
kungl., kungliga
maj:t, majestät
maj:ts, majestäts
ang., angående
t.f., tillförordnad
dvs., det vill säga
febr., februari
apr., april
jun., juni
aug., augusti
sept., september
okt., oktober
nov., november
dec., december
""".split("\n") if len(line) > 1]


def mkabbrevs():
    abbrevs = []
    for exp, rep in abbreviations:
        exp = r"(?:\s|\()" + exp.replace(r".", r"\.\s*")
        if exp[-3:] == r"\s*":
            exp = exp[:-3] + r"(?:\s|,)"
        else:
            exp += r"(?:\s|,)"
        rep = " " + rep + " "
        abbrevs.append((re.compile(exp, re.IGNORECASE), rep))
    # Remove dots from undefined abbrevs
    abbrevs.append((re.compile(r"(?<=\s|\.)([A-ZÅÄÖ][A-ZÅÄÖa-zåäö]{,1}|[a-zåäö])\."), r"\1"))
    return abbrevs


subs_abbrev = mkabbrevs()
