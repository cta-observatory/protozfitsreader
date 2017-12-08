#!/bin/python
from setuptools import setup
setup(
    name='protzfitsreader',
    version='0.41',
    description='Basic python bindings for protobuf zfits reader',
    author="Etienne Lyard et al.",
    author_email="etienne.lyard@unige.ch",
    data_files=[(
        'protzfitsreader', [
            'protzfitsreader/*.so*',
        ])
    ],
    install_requires=['numpy', 'protobuf'],
    packages=['protzfitsreader'],
)
