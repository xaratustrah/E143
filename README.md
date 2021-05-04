# E143 Scripts and Codes

This is the repository for the scripts during the run of the E143 experiment: Search for the nuclear two-photon decay in swift fully-stripped heavy ions.

### Dependencies

These scripts depend on the [IQTools]() library. So please follow the installation instructions [there](https://github.com/xaratustrah/iqtools#install--uninstall).


## e143_looper.py

This script will run on the server, monitor a directory and process them as the files come in. The processing contains the conversion to ROOT files, making an spectrogram in a PNG file, and then copy all files to a (remote) directory. Parameters are:

* `-l` provides the log file to save the already copied files, will be created if not available
* `-p` is the remote path, default is '.'. This remote path can also be the mount point of a remote server, like mounted with SSHFS.

and there is one mandatory command line argument which is the path to keep monitoring. For better operation please provide *full paths*.

    python /home/myuser/git/e143-scripts/e143_looper.py -l '/data.local1/mylogfile.txt' -p '/home/myuser/E143-WWW/dummy/yummy' '/data.local1/dummy-sync'

When calling on the shell, large paths can also be put inside quotation marks "" to avoid complications with respect to paths that include a space in them.

#### Structure of ROOT files

The structure of the root files is like this: there are two trees inside, one tree has only one branch with an integer in it, which is the sampling rate. the other tree also has a branch in it, which contains the time series, which correspond to the power of the signal, meaning sqrt(I^2+Q^2). The distance between the time samples is 1/(sampling_rate).

Inside ROOT you can just read the tree and after making FFT plot them on a histogram, or you can create a 2D histogram if needed.

For more info on ROOT please check the official [CERN ROOT web site](https://root.cern/). If you are interested in using ROOT with minimal installation effort, you can use it under the Python environment and conda forge by following the simple [instructions here](https://iscinumpy.gitlab.io/post/root-conda/).



## e143_analyzer.py

This script can run on any computer with the raw data on it and will be run manually. It traverses through many files, reads an amount of data corresponding to a certain amount of time, makes a 1D-spectrum, adds them up, then makes a PNG plot as well as 1D-ROOT file. Parameters are:

* `-t` amount of time to read from the file in seconds

and there is one mandatory command line argument which is the files to analyse. Here you can use the shell wildcard to provide as many as you wish. Since most data have a time stamp, you can provide a wildcard at the proper place, i.e. if your filenames are like:

    E143-410MHz_-2021.04.30.20.03.01.765.tiq

then you can chose a wildcard at the proper place

    E143-410MHz_-2021.04.* --> all month
    E143-410MHz_-2021.04.30.* --> all day
    E143-410MHz_-2021.04.30.20.* --> all hour
    E143-410MHz_-2021.04.30.20.03.* --> all minute

and so on. Of course other combinations are possible, or you can just list files on the command line. E.g. running:

    python /home/myuser/git/e143-scripts/e143_looper.py -t 0.5 E143-410MHz_-2021.04.30.20.*

will process all files from the last hour, only considering their first 500 ms worth of data.
