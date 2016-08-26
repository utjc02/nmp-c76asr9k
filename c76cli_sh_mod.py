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

    m = re.search('a\d\d\d\-(asr)|(xsw)|(sr)|(cr)0[123]', file)
    if m:
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

wb = xlwt.Workbook()
XL = wb.add_sheet('NMP-PRE')

## HEADER

font0 = xlwt.Font()
font0.name = 'Arial'
font0.colour_index = xlwt.Style.colour_map['blue']
font0.bold = True
font0.height = 240

align0 = xlwt.Alignment()
align0.horz = xlwt.Alignment.HORZ_CENTER
align0.horz = xlwt.Alignment.VERT_CENTER

pattern0 = xlwt.Pattern()
pattern0.pattern = xlwt.Pattern.SOLID_PATTERN
pattern0.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']

style0 = xlwt.XFStyle()
style0.font = font0
style0.alignment = align0
style0.pattern = pattern0

## HOSTNAME
font2 = xlwt.Font()
font2.name = 'Arial'
font2.colour_index = xlwt.Style.colour_map['black']
font2.bold = True
font2.height = 240

align2 = xlwt.Alignment()
align2.horz = xlwt.Alignment.HORZ_CENTER

pattern2 = xlwt.Pattern()
pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
pattern2.pattern_fore_colour = xlwt.Style.colour_map['gray25']

style2 = xlwt.XFStyle()
style2.font = font2
style2.alignment = align2
style2.pattern = pattern2

## NORMAL
font1 = xlwt.Font()
font1.name = 'Arial'
font1.colour_index = xlwt.Style.colour_map['black']
font1.bold = False
font1.height = 240

align1 = xlwt.Alignment()
align1.horz = xlwt.Alignment.HORZ_RIGHT

style1 = xlwt.XFStyle()
style1.font = font1
style1.alignment = align1

## WRITE SHEET HEADER
XL.write_merge(0, 1, 0, 0, 'Hostname', style0)
XL.write_merge(0, 1, 1, 1, 'Version', style0)
XL.write_merge(0, 0, 2, 4, 'Platform', style0)
XL.write_merge(0, 0, 5, 9, 'CDP', style0)
XL.write_merge(0, 0, 10, 12, 'HSRP', style0)

XL.write(1, 2, 'nSUP720', style0)
XL.write(1, 3, 'nLC6704', style0)
XL.write(1, 4, 'nLC6748', style0)
XL.write(1, 5, 'nCR03', style0)
XL.write(1, 6, 'nCR02', style0)
XL.write(1, 7, 'nSR0i', style0)
XL.write(1, 8, 'nASR0i', style0)
XL.write(1, 9, 'nXSW0i', style0)
XL.write(1, 10, 'nHSRPact', style0)
XL.write(1, 11, 'nHSRPstb', style0)
XL.write(1, 12, 'nHSRPall', style0)

## WRITE SHEET DATA
row = 2
col = 0
for host in data.keys():
    XL.write(row, col, host, style2)
    XL.write(row, col + 1, data[host].get('VERSION'), style1)
    XL.write(row, col + 2, data[host].get('MODULE', {}).get('nSUP720', 'N/A'), style1)
    XL.write(row, col + 3, data[host].get('MODULE', {}).get('nLC6704', 'N/A'), style1)
    XL.write(row, col + 4, data[host].get('MODULE', {}).get('nLC6748', 'N/A'), style1)
    XL.write(row, col + 5, data[host].get('CDP', {}).get('nCR03', 'N/A'), style1)
    XL.write(row, col + 6, data[host].get('CDP', {}).get('nCR02', 'N/A'), style1)
    XL.write(row, col + 7, data[host].get('CDP', {}).get('nSR0i', 'N/A'), style1)
    XL.write(row, col + 8, data[host].get('CDP', {}).get('nASR0i', 'N/A'), style1)
    XL.write(row, col + 9, data[host].get('CDP', {}).get('nXSW0i', 'N/A'), style1)
    XL.write(row, col + 10, data[host].get('HSRP', {}).get('nHSRPact', 'N/A'), style1)
    XL.write(row, col + 11, data[host].get('HSRP', {}).get('nHSRPstb', 'N/A'), style1)
    XL.write(row, col + 12, data[host].get('HSRP', {}).get('nHSRPall', 'N/A'), style1)
    row += 1

## SAVE FILE
wb.save("mgts-nmp-py-test-style-3.xls")



