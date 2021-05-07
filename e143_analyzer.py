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


LFRAMES = 1024
SPAN = None
# SPAN = 5000


def process_loop(filenames_list, analysis_time, skip_time, result_filename):
    """
    main processing loop
    """
    try:
        ff = np.array([])
        pp = np.array([])
        for filename in filenames_list:
            print('Processing ', filename)
            iq = get_iq_object(filename)
            iq.read_samples(1)
            lframes = LFRAMES
            nframes = int(analysis_time * iq.fs / lframes)
            sframes = int(skip_time * iq.fs / lframes)
            if nframes >= iq.nsamples_total or sframes >= iq.nsamples_total:
                print(
                    "The chosen analysis or skip time is larger than this file's total length. Aborting...")
                sys.exit()
            iq.read(nframes=nframes, lframes=lframes, sframes=sframes)
            iq.method = 'mtm'
            ff, p, _ = iq.get_fft()
            pp = p if pp.size == 0 else pp + p
        print('Plotting into a png file...')
        plot_spectrum(ff, pp, cen=iq.center, span=SPAN,
                      filename=result_filename, dbm=True, title=result_filename)
        print('Creating a root file...')
        write_spectrum_to_root(ff, pp, filename=result_filename,
                               center=iq.center, title=result_filename)

    except KeyboardInterrupt:
        print(
            "\nOh no! You don't want me to continue analyzing files! Aborting as you wish :-(")


def main():
    scriptname = 'e143_analyzer'
    __version__ = 'v0.0.1'

    default_outfilename = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', type=str, nargs='+',
                        help='Filenames to be processed.')
    parser.add_argument('-t', '--time', nargs='?', type=str, default='1',
                        help='Analysis time from the begining.')
    parser.add_argument('-s', '--skip', nargs='?', type=str, default='0',
                        help='Start of analysis.')
    parser.add_argument('-o', '--outfile', nargs='?', type=str, default=default_outfilename,
                        help='Name of the output file.')

    args = parser.parse_args()

    print('{} {}'.format(scriptname, __version__))

    # allow only TIQ files
    filenames_list = [s for s in args.filenames if s.lower().endswith('tiq')]
    try:
        analysis_time = float(args.time)
        skip_time = float(args.skip)
    except ValueError:
        print('Please provide a number in seconds, like 0.3 or 2. Aborting...')
        sys.exit()

    process_loop(filenames_list, analysis_time, skip_time, args.outfile)


# ------------------------
if __name__ == '__main__':
    main()
