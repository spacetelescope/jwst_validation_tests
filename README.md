# JWST Validation Tests

[![Build Status](https://travis-ci.com/spacetelescope/jwst_validation_tests.svg?branch=master)](https://travis-ci.com/spacetelescope/jwst_validation_tests)
[![PyPI - License](https://img.shields.io/pypi/l/Django.svg)](https://github.com/spacetelescope/jwql/blob/master/LICENSE)
[![STScI](https://img.shields.io/badge/powered%20by-STScI-blue.svg?colorA=707170&colorB=3e8ddd&style=flat)](http://www.stsci.edu)

This repository contains test scripts that are used to validate the output of the JWST Calibration Pipeline. These are tests that do not need to be inspected visually by members
of the science instrument teams (those tests are stored in Jupyter notebooks). To see the JWST Validation Test Notebooks, visit [this repository.](https://github.com/spacetelescope/jwst_validation_notebooks)

These tests follow a consistent [style guide](https://github.com/spacetelescope/style-guides/blob/master/guides/jupyter-notebooks.md) in terms of layout/structure, coding conventions etc.

### Installing the JWST Calibration Pipeline ###
To execute the scripts locally, you must install the JWST Pipeline using [conda](https://conda.io/docs/index.html):

    conda create -n jwst --file <URL>
    source activate jwst

where `<URL>` is of the form:

    Linux: http://ssb.stsci.edu/releases/jwstdp/0.12.2/latest-linux
    OS X: http://ssb.stsci.edu/releases/jwstdp/0.12.2/latest-osx
    
Other versions can be installed by choosing a different version tag in place of "0.12.2" in the URL path. See the "Software vs DMS build version map" table [on this page](https://github.com/spacetelescope/jwst#software-vs-dms-build-version-map) for a list of tags corresponding to particular releases. 

### CRDS Setup ###

Inside the STScI network, the pipeline works with default CRDS setup with no modifications.  To run the pipeline outside the STScI network, CRDS must be configured by setting two environment variables:

    export CRDS_PATH=$HOME/crds_cache
    export CRDS_SERVER_URL=https://jwst-crds.stsci.edu

## Software Contributions

If you would like to contribute to the `jwst_validation_tests` collection, please follow our example of a best work flow for contributing to the project:

1. Create a fork off of the `spacetelescope` `jwst_validation_tests` repository.
2. Make a local clone of your fork.
3. Ensure your personal fork is pointing `upstream` properly.
4. Create a branch on that personal fork.
5. Make your software changes.
6. Push that branch to your personal GitHub repository (i.e. `origin`).
7. On the `spacetelescope` `jwst_validation_tests` repository, create a pull request that merges the branch into `spacetelescope:master`.
8. Assign a reviewer from the team for the pull request.
9. Iterate with the reviewer over any needed changes until the reviewer accepts and merges your branch.
10. Delete your local copy of your branch.


## Issue Reporting / Feature Requests

Users who wish to report an issue or request a new feature may do so by submitting a new issue on GitHub: https://github.com/spacetelescope/jwst_validation_tests/issues
