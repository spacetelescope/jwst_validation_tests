# JWST Validation Tests

<!-- [![Build Status](https://travis-ci.com/spacetelescope/jwst_validation_notebooks.svg?branch=master)](https://travis-ci.com/spacetelescope/jwst_validation_notebooks) -->

This repository contains test scripts that are used to validate the output of the JWST Calibration Pipeline. These are tests that do not need to be inspected visually by members
of the science instrument teams.

These tests follow a consistent [style guide](https://github.com/spacetelescope/style-guides/blob/master/guides/jupyter-notebooks.md) in terms of layout/structure, coding conventions etc.

### Installing the JWST Calibration Pipeline ###
To execute the scripts locally, you must install the JWST Pipeline using [conda](https://conda.io/docs/index.html):

    conda create -n jwst --file <URL>
    source activate jwst

where `<URL>` is of the form:

    Linux: http://ssb.stsci.edu/releases/jwstdp/0.12.2/latest-linux
    OS X: http://ssb.stsci.edu/releases/jwstdp/0.12.2/latest-osx

### CRDS Setup ###

Inside the STScI network, the pipeline works with default CRDS setup with no modifications.  To run the pipeline outside the STScI network, CRDS must be configured by setting two environment variables:

    export CRDS_PATH=$HOME/crds_cache
    export CRDS_SERVER_URL=https://jwst-crds.stsci.edu
