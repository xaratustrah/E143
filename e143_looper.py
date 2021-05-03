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
import shutil
from iqtools import *

# How often to check for new files?
SLEEP = 3  # [s]


def process_loop(directory, wwwpath, logfilename):
    """
    main loop
    """
    for file in os.listdir(directory):
        if file.lower().endswith('.tiq'):
            fullfilename = os.path.join(directory, file)
            if not already_processed(fullfilename, logfilename):
                if not has_handle(fullfilename):
                    process_each(fullfilename)
                    put_into_logfile(fullfilename, logfilename)
                    copy_files_to_wwwpath(fullfilename, wwwpath)


def process_each(filename):
    """
    what to do with each file
    """

    print('Processing ', filename)
    iq = get_iq_object(filename)
    iq.read_samples(1)
    lframes = 1024
    nframes = int(iq.nsamples_total / lframes)
    iq.read(nframes=nframes, lframes=lframes)
    iq.method = 'mtm'
    xx, yy, zz = iq.get_spectrogram(nframes=nframes, lframes=lframes)
    plot_spectrogram(xx, yy, zz, cen=iq.center, filename=filename)

    with uproot3.recreate(filename + '.root') as f:
        f['info_tree'] = uproot3.newtree(
            {'sampling_freq': uproot3.newbranch(np.int32, title='Sampling frequency')})
        f['data_tree'] = uproot3.newtree(
            {'power': uproot3.newbranch(np.float64, title='Time domain signal power')})
        f['info_tree'].extend({'sampling_freq': np.array([int(iq.fs)])})
        f['data_tree'].extend({'power': np.abs(iq.data_array)**2})


def copy_files_to_wwwpath(filename, wwwpath):
    """
    copy the data on the mounted filesystem
    """

    shutil.copy(filename, wwwpath)
    shutil.copy(filename + '.root', wwwpath)
    shutil.copy(filename + '.png', wwwpath)


def put_into_logfile(file, logfilename):
    """
    Write into the log file.
    """

    with open(logfilename, 'a') as file_object:
        file_object.write(file + '\n')


def already_processed(currentfilename, logfilename):
    """
    check whether the file is already in the log file
    """

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
    """
    Check whether the file is not finished copying.
    thanks to:
    https://stackoverflow.com/a/44615315/5177935
    works only under linux
    """

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
                        help='Name of the file for tracking the list of processed files. Use full paths')
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
            # Make sure there is a trailing slash at the end of the path
            monitor_directory = os.path.join(args.monitor_directory, '')
            wwwpath = os.path.join(args.wwwpath, '')
            process_loop(monitor_directory, wwwpath, args.logfile)
            time.sleep(SLEEP)
            print('I am waiting for new files...')

    except KeyboardInterrupt:
        print(
            "\nOh no! You don't want me to continue waiting for new files! Aborting as you wish :-(")


# ------------------------
if __name__ == '__main__':
    main()
