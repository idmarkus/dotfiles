import re
from unidecode import unidecode

_digits = {
    0: "noll",
    1: "ett",
    2: "två",
    3: "tre",
    4: "fyra",
    5: "fem",
    6: "sex",
    7: "sju",
    8: "åtta",
    9: "nio",
    10: "tio",
    11: "elva",
    12: "tolv",
    13: "tretton",
    14: "fjorton",
    15: "femton",
    16: "sexton",
    17: "sjutton",
    18: "arton",
    19: "nitton"
}

_ordinals = {
    0: "nollte",
    1: "första",
    2: "andra",
    3: "tredje",
    4: "fjärde",
    5: "femte",
    6: "sjätte",
    7: "sjunde",
    8: "åttonde",
    9: "nionde",
    10: "tionde",
    11: "elfte",
    12: "tolfte",
    13: "trettonde",
    14: "fjortonde",
    15: "femtonde",
    16: "sextonde",
    17: "sjuttonde",
    18: "artonde",
    19: "nittonde"
}

_tens = {
    0: "",
    2: "tjugo",
    3: "trettio",
    4: "fyrtio",
    5: "femtio",
    6: "sextio",
    7: "sjuttio",
    8: "åttio",
    9: "nittio"
}

_powers = {
    0: "tusen",
    1: "mil",
    2: "bil",
    3: "tril",
    4: "kvadril",
    5: "kvintil",
    6: "sextil",
    7: "septil",
    8: "oktil",
    9: "nonil",
    10: "decil",
    11: "undecil",
    12: "duodecil",
}


def power_word(pwr):
    if pwr == 0: return ""
    if pwr == 1: return "tusen"

    base = _powers[pwr // 2]
    base += "jon" if pwr % 2 == 0 else "jard"

    return base


def spell_hundred(n, pwr, spaces=False, ordinal=False):
    if (n == 0): return ""
    tail = power_word(pwr)
    space = " " if spaces else ""
    if (n > 1):
        if pwr > 1: tail += "er"
        hundra, tio, en = (int(x) for x in f"{n:03}")
        base = ""
        # if hundra > 1 or not ordinal:
        if hundra > 0: base += _digits[hundra]
        if hundra != 0:
            base += space + "hundra"
            if ordinal and tio == 0 and en == 0:
                base += "de"
        if tio > 1:
            if n >= 100: base += space
            base += _tens[tio]
            if ordinal:
                base += space + _ordinals[en] if en > 0 else "nde"
            else:
                base += space + _digits[en] if en > 0 else ""
        elif tio == 1 or en > 0:  # tio == 1 or en > 0: # tio == 1
            if n >= 100: base += space
            if ordinal:
                base += _ordinals[(tio * 10) + en]
            else:
                base += _digits[(tio * 10) + en]
    else:
        if pwr == 0 and ordinal: return "första"
        base = "ett" if (pwr < 2) else "en"
        if (not spaces) and pwr < 2 and len(tail) > 0 and tail[0] == 't': base = "et"
    if spaces:
        return base + " " + tail
    else:
        return base + tail


def spell_number(n, spaces=False, asciify=False, ordinal=False):
    if not n.isnumeric(): return ""
    if int(n) == 0: return "noll"
    word = u""
    space = " " if spaces else ""
    late_ordinal = False
    for i in range(len(n) // 3 + 1):

        if i == 0:
            m = n[-3 * (i + 1):]
        else:
            m = n[-3 * (i + 1):-3 * i]

        if m == '': break
        if int(m) > 0:
            word = spell_hundred(int(m), i, spaces=spaces, ordinal=ordinal) + space + word
        else:
            late_ordinal = ordinal

        ordinal = False
    if late_ordinal:
        word += "de"

    if asciify:
        return unidecode(word)
    else:
        return word


def spell_ordinal(n, spaces=False, asciify=False):
    if not n.isnumeric(): raise "Non numeric number: {}".format(n)
    if n == "0": return "nollte"
    return spell_number(n, spaces=spaces, asciify=asciify, ordinal=True)


def spell_year(n):
    if not n.isnumeric(): raise "Non numeric year: {}".format(n)
    m = f"{int(n):04}"
    h = int(m[:2])
    t = int(m[2:])

    if h < 20:
        hw = spell_hundred(h, 0)
        tw = spell_hundred(t, 0)
        mid = "hundra" if h > 0 else ""
    else:
        if n[1:4] == "000":
            return spell_number(n)
        hw = spell_hundred(h, 0)
        tw = spell_hundred(t, 0)
        mid = "hundra" if (t < 20 and h < 31) or t > 30 else ""
    return hw + mid + tw


if __name__ == "__main__":
    test = "11435872"
    test_t = "elva miljoner fyrahundratrettiofem tusen åttahundrasjuttiotvå"

    test2 = "543272984011"
    test2_t = "femhundrafyrtiotre miljarder tvåhundrasjuttiotvå miljoner niohundraåttiofyra tusen elva"
    test3 = "1152"
    test4 = "223154"
    test5 = "24"

    tests = [
        "11435872",
        "543272984011",
        "1152",
        "223000",
        "24",
        "1",
        "0",
        "112",
        "1003",
        "100",
        "1000",
        "103",
        "10000",
        "1000000"
    ]

    # import sys
    # sys.setdefaultencoding('utf-8')
    for i, test in enumerate(tests):
        spaces = False
        print(test, spell_number(test, spaces=spaces))
        print("  ", spell_ordinal(test, spaces=spaces))

    years = [
        "1102",
        "4",
        "0",
        "1776",
        "1994",
        "2001",
        "2004",
        "2000",
        "1600",
        "2028",
        "2035",
        "2054",
        "4514",
        "872",
        "107"
    ]
    for y in years:
        print(y, spell_year(y))
    # spell(test)
    # spell(test2)
    # spell(test3)
    # spell(test5)

    # print(test, spell_number(test, spaces=True))
    # print(test2, spell_number(test2, spaces=True))
    # print(test3, spell_number(test3, spaces=True))
    # print(test4, spell_number(test4, spaces=True))
    # print(test5, spell_number(test5, spaces=True))
    # print(spell_number(test, spaces=True))
    # print(spell_number(test, spaces=True))
