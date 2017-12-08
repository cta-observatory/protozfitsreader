# Protozftisreader

This repo is currently just a test

## installation:

    conda create -n pz python=3.5
    source activate pz
    pip install git+https://github.com/dneise/protozfitsreader

The contents of this repo come entirely from

http://www.isdc.unige.ch/~lyard/repo/ProtoZFitsReader-0.42.Python3.5.Linux.x86_64.tar.gz


### setup.py

I just updated the setup.py a little to use setuptools instead of distutils.
The result is that all `*.py` and `*.so` files of this package are installed
into a folder called "protozfitsreader" inside the "site-packages",
before the files were directly copied into "site-packages" which worked as well,
but was a little untidy.

### relative imports

As a result, I had to modify some `import` statement, they were written as
absolute imports, but now we do relative imports from the "protozfitsreader"
package.


### set RPATH

The main purpose of this was, to deliver "patched" so-files. The so-files
in the original tar-ball contain absolute RPATHs, which prevent the linker from
finding the dependencies. Here I simply patched the so-files and added relative
RPATH like this:

    patchelf --set-rpath '$ORIGIN' some-file.so

I patched these files:

 * rawzfitsreader.cpython-35m-x86_64-linux-gnu.so
 * libACTLCore.so
 * libZFitsIO.so


These are all differences between this repo and the tar-ball.

# Next steps?

At some point I assume we will merge some or all of these modifications
into the main SVN, but I needed this repo to try the stuff out and also have other people
try it out.

