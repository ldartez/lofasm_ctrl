#!/usr/bin/python


from distutils.core import setup
from glob import glob
import os

BASE_DIR = os.path.dirname(__file__)

setup(
    name='lofasm_ctrl',
    version='0.1',
    author=['Louis P. Dartez'],
    author_email='louis.dartez00 (at) gmail (dot) com',

    packages=['lofasm_ctrl'],
    scripts=glob(os.path.join(BASE_DIR, 'bin/*')),
    data_files=[
        (os.path.join(os.environ['HOME'], '.lofasm'), ['lofasm.cfg']),
    ],
    description='LoFASM Control Scripts',
    long_description=open('README.md').read(),
)
