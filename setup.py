#!/bin/python
from setuptools import setup

with open('protozfitsreader/VERSION') as f:
    __version__ = f.read().strip()

setup(
    name='protozfitsreader',
    packages=['protozfitsreader'],
    version=__version__,
    description='Basic python bindings for protobuf zfits reader',
    author="Etienne Lyard et al.",
    author_email="etienne.lyard@unige.ch",
    package_data={
        'protozfitsreader': [
            '*.so*',
            '*.dylib'
        ],
        '': [
            'VERSION',
            'tests/resources/*'
        ],
    },
    install_requires=['numpy', 'protobuf'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
