# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from stablemarriage import __version__

with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name='stablemarriage',
    version=__version__,
    description='Telecommunication networks fundamentals assignment at UNIFI',
    long_description=README,
    license=LICENSE,
    author='Leonardo Calbi, Alessio Falai',
    author_email='leonardo.calbi@stud.unifi.it, alessio.falai@stud.unifi.it',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7'
    ],
    python_requires='>=3.6',
    keywords='unifi networks project',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'stablemarriage = stablemarriage.stable_marriage:main'
        ]
    }
)
