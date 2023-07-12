from pathlib import Path

input_d = Path("test")
inputs = input_d.glob("*.csv")

output_p = Path("TEST_unicodecharacters.txt")

found = u""
for input_p in inputs:
    print(input_p, flush=True)
    with open(input_p, "r", encoding="utf-8") as f:
        data = f.read()
        for char in data:
            if not char.isascii() and char not in found:
                found += char + "\n"
        with open(output_p, "w+", encoding="utf-8") as f2:
            f2.write(found)
