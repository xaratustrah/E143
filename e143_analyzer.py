#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Process several files as given in the command line argument

2021 Xaratustrah
'''

import sys
import argparse
import datetime
from iqtools import *


def process_loop(filenames_list, analysis_time):
    """
    main processing loop
    """
    try:
        for filename in filenames_list:
            print('Processing ', filename)
            iq = get_iq_object(filename)
            iq.read_samples(1)
            lframes = 1024
            nframes = int(analysis_time * iq.fs / lframes)
            if nframes >= iq.nsamples_total:
                print(
                    "The chosen analysis time is larger than this file's total length. Aborting...")
                sys.exit()
            iq.read(nframes=nframes, lframes=lframes)
            iq.method = 'mtm'
            ff, pp, _ = iq.get_fft()
            pp += pp
        print('Plotting into a png file...')
        result_filename = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
        plot_spectrum(ff, pp, cen=iq.center,
                      filename=filename, dbm=True, title=result_filename)
        print('Creating a root file...')
        write_spectrum_to_root(ff, pp, filename=filename,
                               center=iq.center, title=result_filename)

    except KeyboardInterrupt:
        print(
            "\nOh no! You don't want me to continue analyzing files! Aborting as you wish :-(")


def main():
    scriptname = 'e143_analyzer'
    __version__ = 'v0.0.1'

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', type=str, nargs='+',
                        help='Filenames to be processed.')
    parser.add_argument('-t', '--time', nargs='?', type=str, default='1',
                        help='Analysis time from the begining.')

    args = parser.parse_args()

    print('{} {}'.format(scriptname, __version__))

    # allow only TIQ files
    filenames_list = [s for s in args.filenames if s.lower().endswith('tiq')]
    try:
        analysis_time = float(args.time)
    except ValueError:
        print('Please provide a number in seconds, like 0.3 or 2. Aborting...')

    process_loop(filenames_list, analysis_time)


# ------------------------
if __name__ == '__main__':
    main()
