from pathlib import Path
import mimetypes
import re
import itertools

# For hashing operation steps
from dis import dis
import hashlib

"""
All files in directory as input
  pipe = Pipeline("~/data")

Glob or custom glob of file mimetype
  pipe = Pipeline("data0/*.image",
                  "data1/*.video",
                  "data2/*.text"
                  "data3/*.csv")
  
pipe.op(func1)



"""

# class Pipeline:
#     # def __glob(self, x):
#
#
#
#     def __init__(self, *args):
#
