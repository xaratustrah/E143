#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Process files as they are copied one by one
Linux-only script due to proc

2021 Xaratustrah
'''

import os
import argparse
import datetime
import time
import platform
if platform.system() == 'Linux':
    import psutil

from iqtools import *

SLEEP = 3  # [s]


def process_loop(directory, wwwpath, logfilename):
    for file in os.listdir(directory):
        if file.lower().endswith('.tiq'):
            fullfilename = os.path.join(directory, file)
            if not already_processed(fullfilename, logfilename):
                if not has_handle(fullfilename):
                    process_each(fullfilename)
                    put_into_logfile(fullfilename, logfilename)


def process_each(filename):
    print('Processing ', filename)
    get_png_plot(filename)
    get_root_file(filename)
    copy_files_to_wwwpath()


def copy_files_to_wwwpath():
    pass


def get_root_file(filename):
    pass


def get_png_plot(filename):
    iq = get_iq_object(filename)
    iq.read_samples(1)
    lframes = 1024
    nframes = int(iq.nsamples_total / lframes)
    iq.read(nframes=nframes, lframes=lframes)
    iq.method = 'mtm'
    xx, yy, zz = iq.get_spectrogram(nframes=nframes, lframes=lframes)
    plot_spectrogram(xx, yy, zz, cen=iq.center, filename=filename)


def put_into_logfile(file, logfilename):
    with open(logfilename, 'a') as file_object:
        file_object.write(file + '\n')


def already_processed(currentfilename, logfilename):
    already_processed = False
    try:
        with open(logfilename, 'r') as file_object:
            loglist = file_object.readlines()

            for line in loglist:
                if currentfilename in line:
                    already_processed = True

    except OSError as e:
        print('Log file does not exist, creating a new one.')

    return already_processed


def has_handle(fpath):
    # The following function thanks to:
    # https://stackoverflow.com/a/44615315/5177935
    # works only under linux
    if platform.system() == 'Linux':
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if fpath == item.path:
                        return True
            except Exception:
                pass
        return False
    else:
        pass


def main():
    scriptname = 'e143_looper'
    __version__ = 'v0.0.1'

    default_logfilename = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S') + '.txt'
    parser = argparse.ArgumentParser()
    parser.add_argument('monitor_directory', type=str,
                        help='Name of the directory to monitor for files. Use full paths.')
    parser.add_argument('-l', '--logfile', nargs='?', type=str, default=default_logfilename,
                        help='Name of the file for tracking the list of processed files. Use full paths.')
    parser.add_argument('-p', '--wwwpath', nargs='?', type=str, default='./',
                        help='Remote path to WWW server. Use full paths.')

    args = parser.parse_args()

    print('{} {}'.format(scriptname, __version__))

    print('Processing files in directory: ', args.monitor_directory)
    print('Remote path will be: ', args.wwwpath)
    print('Log file will be: ', args.logfile)

    print('Let us see if there are new files...')

    try:
        while True:
            process_loop(args.monitor_directory, args.wwwpath, args.logfile)
            time.sleep(SLEEP)
            print('I am waiting for new files...')

    except KeyboardInterrupt:
        print(
            "Oh no! You don't want me to continue waiting for new files! Aborting you wish :-(")


# ------------------------
if __name__ == '__main__':
    main()
