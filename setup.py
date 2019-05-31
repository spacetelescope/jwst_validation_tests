#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='jwst_validation_tests',
    version = '0.1',
    description = 'JWST Calibration Pipeline Validation Tests',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/spacetelescope/jwst_validation_tests",
    author = 'Pipeline Testing Focus Group',
    author_email = 'acanipe@stsci.edu',
    keywords = ['astronomy'],
    classifiers = ['Programming Language :: Python :: 3'],
    packages = find_packages(exclude=["examples"]),
    install_requires = [],
    include_package_data = True
    )
