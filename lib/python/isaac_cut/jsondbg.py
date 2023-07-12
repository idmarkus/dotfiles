import json

from pathlib import Path
from pprint import pprint

in_p = Path("./uncut/") / "W0NP B4DDEden.json"
out_p = Path("./uncut/") / "W0NP_pretty.json"
with open(in_p) as f:
    info = json.load(f)

if not out_p.exists():
    with open(out_p, "w") as f:
        json.dump(info, f, indent=4, sort_keys=True)

from cuthelpers import *

rooms = Rooms(info["rooms"], info["obs_starttime"])

for r in rooms:
    if r["stage"] == 9:
        pprint(r)
# firstseen = Counter([str("{}:{}".format(x["stage"], x["roomIndex"])) for x in info["rooms"] if x["isFirstVisit"] == True])
# for v in firstseen.most_common(20):
#     print(v, flush=True)
# for r in info["rooms"]:
#     if r["stage"] != 9:
#         continue
#     pprint(r)
