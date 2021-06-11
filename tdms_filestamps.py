#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Extract the time stamp information in TDMS file directory

2021 Xaratustrah
'''

import os
import glob
import csv
import datetime

CONST = 53.6870912

beginn = os.getcwd().split('/')[-1]

try:
    dt = datetime.datetime.strptime(beginn, 'IQ_%Y-%m-%d_%H-%M-%S')

    timestamps = []
    for i in glob.glob("*.tdms"):
        seconds = int(i.split('.')[0]) * CONST
        newtime = dt + datetime.timedelta(seconds=seconds)
        timestamps.append([i, newtime.strftime('%Y.%m.%d.%H.%M.%S.%f')])

    timestamps.sort()

    with open(beginn + '.csv', 'w') as f:
        write = csv.writer(f, delimiter='|')
        write.writerow(['#filename', 'timestamp'])
        write.writerows(timestamps)
except:
    print('Directory date format not matching.')
