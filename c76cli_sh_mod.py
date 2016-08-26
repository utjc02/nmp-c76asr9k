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
import xlwt
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

        ## show version
        if inFileName.endswith(fileNameTypeSuffixVERSION):
            with inFile as inData:
                for rawline in inData:
                    line = rawline.strip()
                    if line.startswith("Cisco IOS Software"):
                        m = re.search('.* Version (\d\d\..*)\, .*', line)
                        if m:
                            version = m.group(1)
                            data[node].update({'VERSION': version})

        ## show module
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
                data[node]["MODULE"].update({'nLC6748': nLC6748})
                data[node]["MODULE"].update({'nSUP720': nSUP720})

        ## show cdp neighbor
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

                data[node]["CDP"].update({'nCR03' : nCR03})
                data[node]["CDP"].update({'nCR02' : nCR02})
                data[node]["CDP"].update({'nSR0i' : nSR0i})
                data[node]["CDP"].update({'nASR0i': nASR0i})
                data[node]["CDP"].update({'nXSW0i': nXSW0i})

        ## show standby
        elif inFileName.endswith(fileNameTypeSuffixHSRP):
            with inFile as inData:
                data[node].update({"HSRP": {}})
                nHSRPact = 0
                nHSRPstb = 0
                nHSRPall = 0
                for rawline in inData:
                    line = rawline.strip()
                    if line.startswith("State is Active"):
                        nHSRPact += 1
                        nHSRPall += 1
                    if line.startswith("State is Standby"):
                        nHSRPstb += 1
                        nHSRPall += 1

                data[node]["HSRP"].update({'nHSRPact' : nHSRPact})
                data[node]["HSRP"].update({'nHSRPstb' : nHSRPstb})
                data[node]["HSRP"].update({'nHSRPall' : nHSRPall})

#print(json.dumps(data, indent = 4))

workbook = xlwt.Workbook()
XL = workbook.add_sheet('NMP-PRE')
XL.write(0, 0, 'Hostname')
XL.write(0, 1, 'Version')
XL.write(0, 2, 'nSUP720')
XL.write(0, 3, 'nLC6704')
XL.write(0, 4, 'nLC6748')
XL.write(0, 5, 'nCR03')
XL.write(0, 6, 'nCR02')
XL.write(0, 7, 'nSR0i')
XL.write(0, 8, 'nASR0i')
XL.write(0, 9, 'nXSW0i')
XL.write(0, 10, 'nHSRPact')
XL.write(0, 11, 'nHSRPstb')
XL.write(0, 12, 'nHSRPall')



row = 1
col = 0
for host in data.keys():
    XL.write(row, col, host)
    print host
    XL.write(row, col + 1, data[host].get('VERSION'))
    XL.write(row, col + 2, data[host].get('MODULE', {}).get('nSUP720', 'NA'))
    XL.write(row, col + 3, data[host].get('MODULE', {}).get('nLC6704', 'NA'))
    XL.write(row, col + 4, data[host].get('MODULE', {}).get('nLC6748', 'NA'))
    XL.write(row, col + 5, data[host].get('CDP', {}).get('nCR03', 'NA'))
    XL.write(row, col + 6, data[host].get('CDP', {}).get('nCR02', 'NA'))
    XL.write(row, col + 7, data[host].get('CDP', {}).get('nSR0i', 'NA'))
    XL.write(row, col + 8, data[host].get('CDP', {}).get('nASR0i', 'NA'))
    XL.write(row, col + 9, data[host].get('CDP', {}).get('nXSW0i', 'NA'))
    XL.write(row, col + 10, data[host].get('HSRP', {}).get('nHSRPact', 'NA'))
    XL.write(row, col + 11, data[host].get('HSRP', {}).get('nHSRPstb', 'NA'))
    XL.write(row, col + 12, data[host].get('HSRP', {}).get('nHSRPall', 'NA'))
    row += 1
workbook.save('mgts-nmp-py-test-3.xls')



