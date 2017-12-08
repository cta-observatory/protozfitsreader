# Protozftisreader

This repo is currently just a test

## installation:

    conda create -n pz python=3.5
    source activate pz
    pip install git+https://github.com/dneise/protozfitsreader

The contents of this repo come from

http://www.isdc.unige.ch/~lyard/repo/ProtoZFitsReader-0.42.Python3.5.Linux.x86_64.tar.gz

I just updated the setup.py a little to use setuptools instead of distutils, but this has no functional effect.

What is different is that I "patched" the `rawzfitsreader.cpython-35m-x86_64-linux-gnu.so` like this

    patchelf --set-rpath '$ORIGIN' rawzfitsreader.cpython-35m-x86_64-linux-gnu.so

That's all.

----

I just uploaded the stuff here into this repo, so other people can try it out
as well.
