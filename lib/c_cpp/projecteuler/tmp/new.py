#! /usr/bin/python
from time import strftime
from subprocess import call
import sys
import os

if not sys.argv[1]:
    sys.exit("No argument.")
else:
    sCwd = os.getcwd()
    lDirs = os.listdir(sCwd)
    sArg1 = sys.argv[1]
    if sArg1 in lDirs:
        sys.exit("Directory for {} already exists".format(sArg1))
 
# Copy the prototype:
call(["cp", "-ri", "./canonical", "./{}".format(sArg1)])
#print("Created {}".format(sArg1))

# Do logging:
sLogsDir = sCwd + "/.logs"

with open(sCwd + "/creation.log", "a") as f:
    f.write(strftime("%F_%T%t")+"Create: {}\n".format(sArg1))
