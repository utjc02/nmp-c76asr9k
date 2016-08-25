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


# DEFAULTS


# DATETIME
start_time = time.time()
now = datetime.datetime.now()
nowDate = now.strftime("%Y%m%d")

data = {}

inDir = '/Users/dzarudni/Documents/csco/CUST/mgts/tasks/2016-08-15 -- Migration76-ASR9k/RawInv50-cli'

for inSubDir in os.walk(inDir):
    pathFull = inSubDir[0]
    path, file = os.path.split(pathFull)
    file = os.path.splitext(file)[0]
    node = file
    data[node] = {}
    fileNameTypeSuffix = "show_version.txt"
    for inFileName in inSubDir[2]:
        if inFileName.endswith(fileNameTypeSuffix):
            inFile = open(pathFull + "/" + inFileName)
            with inFile as inData:
                for rawline in inData:
                    line = rawline.strip()
                    if line.startswith("Cisco IOS Software"):
                        m = re.search('.* Version (\d\d\..*)\, .*', line)
                        if m:
                            version = m.group(1)
                            data[node].update({'VERSION' : version})
print data



