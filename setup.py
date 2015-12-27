#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import botcoin

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='botcoin',
    version=botcoin.__version__,
    url='http://github.com/vergl4s/botcoin/',
    license='Apache Software License',
    author='Luis Teixeira',
    install_requires=['pandas>=0.16.2',
                    'matplotlib>=1.4.3',
                    'numpy==1.9.2',
                    ],
    scripts = ['scripts/live_algo.py', 'scripts/backtest_algo.py', 'scripts/download_symbols.py'],
    author_email='luis@teix.co',
    description='Tradingzzz',
    packages=['botcoin'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    test_suite='tests', 
)
