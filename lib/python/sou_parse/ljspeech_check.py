from pathlib import Path

meta = Path("./LJSpeech/LJSpeech-1.1/metadata.csv")

longest = 0
shortest = 2 ** 32
every = 0
n = 0

longest_str = ""
shortest_str = ""

mostwords = 0
leastwords = 2 ** 32
allwords = 0

mostwords_str = ""
leastowrds_str = ""

with open(meta, 'r', encoding='UTF-8') as f:
    for line in f.readlines():
        sentence = line.split("|")[1]
        length = len(sentence)
        words = len(sentence.split(" "))

        if length > longest:
            longest = length
            longest_str = sentence
        elif length < shortest:
            shortest = length
            shortest_str = sentence
        every += length
        n += 1

        if words > mostwords:
            mostwords = words
            mostwords_str = sentence
        elif words < leastwords:
            leastwords = words
            leastwords_str = sentence
        allwords += words

print("long: {}, short: {}, avg: {}, total: {}".format(longest, shortest, every / n, n))
print("words: most: {}, least: {}, avg: {}".format(mostwords, leastwords, allwords / n))

print(longest_str)
print("")
print(mostwords_str)
print("\n\n")
print(shortest_str)
print("")
print(leastwords_str)
