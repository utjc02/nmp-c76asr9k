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
fileNameTypeSuffixVERSION = "show_version.txt"
fileNameTypeSuffixMODULE = "show_module.txt"
fileNameTypeSuffixHSRP = "show_standby.txt"
fileNameTypeSuffixCDP = "show_cdp_neighbors.txt"

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

    for inFileName in inSubDir[2]:
        inFile = open(pathFull + "/" + inFileName)
        if inFileName.endswith(fileNameTypeSuffixVERSION):
            with inFile as inData:
                for rawline in inData:
                    line = rawline.strip()
                    if line.startswith("Cisco IOS Software"):
                        m = re.search('.* Version (\d\d\..*)\, .*', line)
                        if m:
                            version = m.group(1)
                            data[node].update({'VERSION': version})

        elif inFileName.endswith(fileNameTypeSuffixMODULE):
            with inFile as inData:
                data[node].update({"MODULE": {}})
                inBlock = False
                nSUP720 = 0
                nRSP720 = 0
                nLC6704 = 0
                nLC6748 = 0
                for rawline in inData:
                    line = rawline.strip()
                    if inBlock:
                        if line.startswith("Mod"):
                            inBlock = False
                            break
                        else:
                            m = re.search('.*(WS-X6704.*)\s+.*', line)
                            if m:
                                nLC6704 += 1
                            m = re.search('.*(WS-X6748.*)\s+.*', line)
                            if m:
                                nLC6748 += 1
                            m = re.search('.*(WS-SUP720.*)\s+.*', line)
                            if m:
                                nSUP720 += 1
                    elif line.startswith("---"):
                        inBlock = True
                data[node]["MODULE"].update({'nLC6704': nLC6704})
                data[node].update({'nLC6748': nLC6748})
                data[node].update({'nSUP720': nSUP720})

        elif inFileName.endswith(fileNameTypeSuffixCDP):
            with inFile as inData:
                data[node].update({"CDP": {}})
                nCR03 = 0
                nCR02 = 0
                nSR0i = 0
                nASR0i = 0
                nXSW0i = 0
                for rawline in inData:
                    line = rawline
                    if line.startswith("a"):
                        m = re.search('(a\d\d\d\-cr03).*', line)
                        if m:
                            nCR03 += 1
                        m = re.search('(a\d\d\d\-cr02).*', line)
                        if m:
                            nCR02 += 1
                        m = re.search('(a\d\d\d\-sr0[12345]).*', line)
                        if m:
                             nSR0i += 1
                        m = re.search('(a\d\d\d\-asr0[12]).*', line)
                        if m:
                             nASR0i += 1
                        m = re.search('(a\d\d\d\-xsw0[1234]).*', line)
                        if m:
                             nXSW0i += 1

                data[node].update({'nCR03' : nCR03})
                data[node].update({'nCR02' : nCR02})
                data[node].update({'nSR0i' : nSR0i})
                data[node].update({'nASR0i': nASR0i})
                data[node].update({'nXSW0i': nXSW0i})

print(json.dumps(data, indent = 4))





