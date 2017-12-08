#!/bin/python
from setuptools import setup
setup(
    name='ProtoZFitsReader',
    version='0.41',
    description='Basic python bindings for protobuf zfits reader',
    author="Etienne Lyard et al.",
    author_email="etienne.lyard@unige.ch",
    data_files=[(
        'lib/python3.5/site-packages', [
            'rawzfitsreader.cpython-35m-x86_64-linux-gnu.so',
            'libZFitsIO.so',
            'libACTLCore.so',
            'libprotobuf.so.9',
            'libzmq.so.3',
        ])
    ],
    install_requires=['numpy', 'protobuf'],
    py_modules=['CoreMessages_pb2', 'L0_pb2', 'protozfitsreader'],
)
