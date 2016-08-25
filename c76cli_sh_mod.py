#!/usr/bin/python

## C7600 sr* nodes config|CLI parsing
## v0.01 -- INIT

from datetime import datetime
from time import strptime
from sys import stdout
import getopt
import collections
import os
import sys
import re
import time
import datetime
import json
import gzip
import shutil
import xlwt

# DEFAULTS
inDir = '../RawInv50-cli'

# DATETIME
start_time = time.time()
now = datetime.datetime.now()
nowDate = now.strftime("%Y%m%d")

inFile = open(inFileName)
data = {}

inDir = '../RawInv50-cli'

for inSubDir in os.walk(inDir):
    path, file = os.path.split(inSubDir[1])
    file = os.path.splitext(file)[1]
    print 'Dir: ' + file



