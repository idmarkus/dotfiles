from pathlib import Path
from sentenize import sentenize
from perf import Perf

if __name__ == "__main__":
    clean_d = Path("cleaned")
    inputs = clean_d.glob("*.csv")

    output_d = Path("sentences")
    output_d.mkdir(exist_ok=True)

    for input_p in inputs:
        fname = input_p.name[:-4]
        if fname == "cleaned_sou_1922-1929": continue

        with open(input_p, "r", encoding="utf-8") as f:
            data = f.read()

        perf = Perf(f"{input_p}")
        sentences = sentenize(data)
        del perf
        print(len(sentences), "sentences", flush=True)
