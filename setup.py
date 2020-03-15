"""FOOOF setup script."""

import os
from setuptools import setup, find_packages

# Get the current version number from inside the module
with open(os.path.join('fooof', 'version.py')) as vf:
    exec(vf.read())

# Copy in long description.
#  Note: this is a partial copy from the README
#    Only update here in coordination with the README, to keep things consistent.
LONG_DESCRIPTION = \
"""
FOOOF: Fitting Oscillations & One-Over F

FOOOF is a fast, efficient, physiologically-informed model to parameterize neural
power spectra, characterizing both the aperiodic & periodic components.

The model conceives of the neural power spectrum as consisting of two distinct components:

1) an aperiodic component, reflecting 1/f like characteristics, modeled with an exponential fit, with
2) band-limited peaks, reflecting putative oscillations, and modeled as Gaussians

The FOOOF codebase includes:

- Code for applying models to parameterize neural power spectra
- Plotting functions for visualizing power spectra, model fits, and model parameters
- Analysis functions for examing model components and parameters
- Utilities for Input/Output management, data management and analysis reports
- Simulation code for simulating power spectra for methods testing

More details on FOOOF tool and codebase are available on the documentation site

Documentation: https://fooof-tools.github.io/

If you use this code in your project, please cite:

Haller M, Donoghue T, Peterson E, Varma P, Sebastian P, Gao R, Noto T, Knight RT, Shestyuk A,
Voytek B (2018) Parameterizing Neural Power Spectra. bioRxiv, 299859. doi: https://doi.org/10.1101/299859

A full description of the method and approach is available in this paper.

Direct Paper Link: https://www.biorxiv.org/content/early/2018/04/11/299859
"""

setup(
    name = 'fooof',
    version = __version__,
    description = 'fitting oscillations & one-over f',
    long_description = LONG_DESCRIPTION,
    python_requires = '>=3.5',
    author = 'The Voytek Lab',
    author_email = 'voyteklab@gmail.com',
    maintainer = 'Thomas Donoghue',
    maintainer_email = 'tdonoghue.research@gmail.com',
    url = 'https://github.com/fooof-tools/fooof',
    packages = find_packages(),
    license = 'Apache License, 2.0',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    platforms = 'any',
    project_urls = {
        'Documentation' : 'https://fooof-tools.github.io/fooof/',
        'Bug Reports' : 'https://github.com/fooof-tools/fooof/issues',
        'Source' : 'https://github.com/fooof-tools/fooof'
    },
    download_url = 'https://github.com/fooof-tools/fooof/releases',
    keywords = ['neuroscience', 'neural oscillations', 'power spectra', '1/f', 'electrophysiology'],
    install_requires = ['numpy', 'scipy>=0.19.0'],
    tests_require = ['pytest'],
    extras_require = {
        'plot'    : ['matplotlib'],
        'tests'   : ['pytest'],
        'all'     : ['matplotlib', 'tqdm', 'pytest']
    }
)
