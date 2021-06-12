#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Plot spectra in ROOT for peak detection

2021 Xaratustrah
'''


import sys
from iqtools import *
from ROOT import TCanvas, TFile, TH1F, TSpectrum
LFRAMES = 2**18
NFRAMES = 2 * 8


def do_plot(filename):
    iq = get_iq_object(filename)
    iq.read_samples(LFRAMES * NFRAMES)
    xx, yy, zz = iq.get_spectrogram(lframes=LFRAMES, nframes=NFRAMES)
    xa, ya, za = iq.get_averaged_spectrum(xx, yy, zz, NFRAMES)
    #ff, pp, _ = iq.get_fft()
    ff = xa[0]
    pp = za[0]
    pp = pp / pp.max()
    h = TH1F('h', 'h', len(ff), iq.center + ff[0], iq.center + ff[-1])
    for i in range(len(ff)):
        h.SetBinContent(i, pp[i])
    f = TFile(filename + '.root', 'RECREATE')
    h.Write()
    f.Close()


def main():
    do_plot(sys.argv[1])


# ------------------------
if __name__ == '__main__':
    main()
