# Protozftisreader [![Build Status](https://travis-ci.org/cta-sst-1m/protozfitsreader.svg?branch=master)](https://travis-ci.org/cta-sst-1m/protozfitsreader)

## installation:

We all use [Anaconda](https://www.anaconda.com/) and this package is tested
against Anaconda. You can [download anaconda](https://www.anaconda.com/download) for your system for free.

You do not have to use a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) to use this package. It cleanly installs and uninstalls with [pip](https://docs.python.org/3.6/installing/). If you plan to play around with different versions of this package your might want to use environments though.

### Faster installation?

You can just `pip install` this, but it will use `pip` to install all the dependencies.
`pip install <some package>` is sometimes much slower than `conda install <some package>`.
So we recommend to

    conda install numpy protobuf

if you don't have that already.

### Linux (with anaconda)

    pip install https://github.com/cta-sst-1m/protozfitsreader/archive/v0.44.0.tar.gz

### OSX (with anaconda)

    pip install https://github.com/cta-sst-1m/protozfitsreader/archive/v0.44.0.tar.gz

To use it you'll have to find your `site-packages` folder, e.g. like this:

    dneise@lair:~$ python -m site
    sys.path = [
        '/home/dneise',
        '/home/dneise/Downloads/rootfoo/build_root/lib',
        '/home/dneise/anaconda3/lib/python36.zip',
        '/home/dneise/anaconda3/lib/python3.6',
        '/home/dneise/anaconda3/lib/python3.6/lib-dynload',
        '/home/dneise/anaconda3/lib/python3.6/site-packages',   <----- this one <-----
    ]

And then you'll have to (put it in your .bashrc for example)

    export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/home/dneise/anaconda3/lib/python3.6/site-packages

### To developers: No `pip --editable`

This package contains pre-build binaries, which (at the moment) are required to be installed
into your "site-packages" folder.
Developers like to install packages they are currently developing like this:

    pip install --editable .

Because then they can modify code and try it out without constant uninstall/install cycles.
Unfortunately this nice development workcycle is not possible at the moment.

I personally do:

    git clone https://github.com/cta-sst-1m/protozfitsreader
    pip install protozfitsreader
    # play around ... modify ...
    pip uninstall protozfitsreader --yes && pip install protozfitsreader
    # play around ... modify ...
    pip uninstall protozfitsreader --yes && pip install protozfitsreader
    # and so on

The uninstall/install takes 1..2sec ... so it is rather ok... not perfect though.



# Where does this come from?

The contents of this repo come entirely from: http://www.isdc.unige.ch/~lyard/repo/

## Modifications with respect to http://www.isdc.unige.ch/~lyard/repo/

1. setup.py:

    I just updated the setup.py a little to use setuptools instead of
    distutils. The result is that all `*.py` and `*.so` files of this package are
    installed into a folder called "protozfitsreader" inside the "site-packages",
    before the files were directly copied into "site-packages" which worked as
    well, but was a little untidy.

2. relative imports

    As a result, I had to modify some `import` statement, they were written as
    absolute imports, but now we do relative imports from the "protozfitsreader"
    package.


3. set RPATH

   The main purpose of this was, to deliver "patched" so-files. The so-files
   in the original tar-ball contain absolute RPATHs, which prevent the linker from
   finding the dependencies. Here I simply patched the so-files and added relative
   RPATH like this:

    ```
    for i in *.so; do patchelf --set-rpath '$ORIGIN' $i; done
    for i in raw*.so; do patchelf --set-rpath '$ORIGIN:$ORIGIN/../../../' $i; done
    for i in *.so; do echo $i; patchelf --print-rpath $i; done
    ```

    gives:
    ```
    libACTLCore.so
    $ORIGIN
    libZFitsIO.so
    $ORIGIN
    rawzfitsreader.cpython-35m-x86_64-linux-gnu.so
    $ORIGIN:$ORIGIN/../../../
    rawzfitsreader.cpython-36m-x86_64-linux-gnu.so
    $ORIGIN:$ORIGIN/../../../
    ```
