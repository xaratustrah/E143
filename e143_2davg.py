#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Average several files as given in the command line argument

2021 Xaratustrah
'''

import sys
import argparse
import datetime
from iqtools import *
from ROOT import TFile

LFRAMES = 1024
result_filename = 'blah'


def process_loop(filenames_list):
    zz = np.array([])
    for filename in filenames_list:
        print('Processing ', filename)
        iq = get_iq_object(filename)
        iq.read_samples(1)
        lframes = LFRAMES
        nframes = int(iq.nsamples_total / lframes)
        iq.read_samples(nframes * lframes)
        z = get_cplx_spectrogram(
            iq.data_array, lframes=lframes, nframes=nframes)
        if np.shape(zz)[0] == 0:
            zz.resize((nframes, lframes))
            zz += np.abs(z)
        else:
            zz += np.abs(z)

    print('Plotting into a png file...')
    # just get the xx and yy from somewhere, ignore zz
    xx, yy, _ = iq.get_spectrogram(lframes=lframes, nframes=nframes)
    # use zz with those xx and yy
    #zz = np.abs(np.fft.fftshift(zz, axes=1))
    plot_spectrogram(xx, yy, np.abs(np.fft.fftshift(zz, axes=1)), filename=result_filename, cen=iq.center,
                     dbm=False, title=result_filename)

    # write a histogram to a file
    print('Writing histogram into a root file...')
    h = get_root_th2d(xx, yy, np.abs(np.fft.fftshift(zz, axes=1)))
    ff = TFile(result_filename + '.root', 'RECREATE')
    h.Write()
    ff.Close()
    inv_zz = get_inv_cplx_spectrogram(zz, lframes=lframes, nframes=nframes)
    print('writing signal as binary')
    write_signal_to_bin(inv_zz, result_filename, fs=iq.fs,
                        center=iq.center, write_header=True)


def main():

    process_loop(sys.argv[1:])


# ------------------------
if __name__ == '__main__':
    main()
