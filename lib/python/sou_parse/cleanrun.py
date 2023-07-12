from pathlib import Path
from clean import clean

if __name__ == "__main__":
    input_d = Path("./sou_dataset/dataset")
    inputs = list(input_d.glob("*.csv"))

    clean(inputs)
