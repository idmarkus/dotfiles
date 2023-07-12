import re

from functools import reduce


def compose(*fs):
    def _compose(f, g):
        return lambda arg: f(g(arg))

    return reduce(_compose, fs)


# abbreviations =\
# u"""
# fr.o.m., från och med
# tekn., teknologie
# dr.|d:r, doktor
# art., artikel
# c:a, cirka
# doc., docent
# d.v.s, det vill säga
# d.y., den yngre
# d.ä., den äldre
# ekon., ekonomi
# f.d., före detta
# fig., figur
# fil., filosofie
# fil.dr., filosofie doktor
# kand., kandidat
# forts., fortsättning
# ggr, gånger
# iaf, i alla fall
# Ibid.|ib., ibid
# i.o.m., i och med
# iofs, i och för sig
# i s.f., i stället för
# jr., junior
# sr., senior
# k:a, kyrka
# lic., licentiat
# m., med
# m.a.o., med andra ord
# mag., magister
# m.m., med mera
# msk, matsked
# tsk, tesked
# m.v.h., med vänlig hälsning
# möjl., möjligen
# m ö.h., meter över havet
# n/a, ej tillämplig
# n.b., nedre botten
# n:o|no., nummer
# näml., nämligen
# nästk., nästkommande
# o.d.|o.dyl., och dylikt
# omkr., omkring
# op., opus
# ordf., ordförande
# orig., original
# o.s.v., och så vidare
# pers., person
# p.g.a., på grund av
# prof., professor
# prov., provisorisk
# ref., referens
# resp., respektive
# s.|sid., sida
# s.a.s., så att säga
# SEK, kronor
# sekr., sekreterare
# s.g.s., så gott som
# s.k., så kallad
# st., styck
# S:t, sankt
# s:ta, sankta
# särsk., särskilt
# tab., tabell
# tel.|tfn, telefon
# temp., temperatur
# teol., teologie
# t.ex., till exempel
# tf., tillförordnad
# t.h., till höger
# tkr, tusen kronor
# mkr, miljoner kronor
# t.o.m., till och med
# t.v., tills vidare
# u.a., utan anmärkan
# u.f.a., under förutsättning att
# urspr., ursprungligen
# ö.a.|övers.anm., översättarens anmärkan
# ö.h., över havet
# ö.h.t., över huvud taget
# övers., översättning
# e.kr., efter kristus
# a.d., efter kristus
# e.g., till exempel
# i.e., det vill säga
# kungl., kungliga
# maj:t, majestät
# prop., proposition
# ang., angående
# """

# def mkabbrevs():
#     _abbrev = []
#     for line in abbreviations.split("\n"):
#         if len(line) < 1: continue
#         exp = line.split(",")[0]
#         exp = r"\s" + exp.replace(r".", r"\.\s*")
#         exp = exp.replace(r".\s*|", r".*\s|")
#         if exp[-4:] == r".\s*": exp = exp[:-4] + r".*\s"
#         else: exp += r"\s"
#         rep = line.split(",")[1][1:]
#         _abbrev.append((re.compile(exp, re.IGNORECASE), rep))
#     return _abbrev

# _abbrev = mkabbrevs()

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
    return abbrevs


abbrevs = mkabbrevs()


def replace_abbrevs(text):
    for exp, rep in abbrevs:
        text = re.sub(exp, rep, text)
    return text


def clean_undefined_abbrevs(text):
    return re.sub(r"(?<=\s|\.)([A-ZÅÄÖ][A-ZÅÄÖa-zåäö]{,1}|[a-zåäö])\.", r"\1", text)


# def mkabbrevs():
#     _abbrev = []
#     for line in abbreviations.split("\n"):
#         if len(line) < 1: continue
#         exp = line.split(",")[0]
#         exp = r"\s" + exp.replace(r".", r"\.\s*")
#         exp = exp.replace(r".\s*|", r".*\s|")
#         if exp[-4:] == r".\s*": exp = exp[:-4] + r".*\s"
#         else: exp += r"\s"
#         rep = line.split(",")[1][1:]
#         _abbrev.append((re.compile(exp, re.IGNORECASE), rep))
#     return _abbrev

# _abbrev = mkabbrevs()


if __name__ == "__main__":
    # print(abbrevs)
    # exit()
    from pathlib import Path

    input_d = Path("./sou_dataset/dataset/sou_2020.csv")
    with open(input_d, "r", encoding="utf-8") as f:
        data = f.read()
        for i, x in enumerate(abbrevs):
            matches = re.findall(x[0], data)
            if len(matches) > 0: print(abbreviations[i][0], len(matches), flush=True)

    exit()


def expand_abbrev(text):
    for regex, replacement in _abbrev:
        text = re.sub(regex, replacement, text)
    return text


# strip_entry = lambda x: re.sub(r"\"\s*\d{4},\d+,\d+,\"", "", x)
breakrow = lambda x: re.sub(r"(\w)-\ (\w)", r"\1\2", x)

cleanup = compose(expand_abbrev, breakrow)
