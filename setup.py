"""FOOOF setup script."""

import os
from setuptools import setup, find_packages

# Get the current version number from inside the module
with open(os.path.join('fooof', 'version.py')) as version_file:
    exec(version_file.read())

# Load the long description from the README
with open('README.rst') as readme_file:
    long_description = readme_file.read()

# Load the required dependencies from the requirements file
with open("requirements.txt") as requirements_file:
    install_requires = requirements_file.read().splitlines()

setup(
    name = 'fooof',
    version = __version__,
    description = 'fitting oscillations & one-over f',
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
    python_requires = '>=3.6',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    platforms = 'any',
    project_urls = {
        'Documentation' : 'https://fooof-tools.github.io/fooof/',
        'Bug Reports' : 'https://github.com/fooof-tools/fooof/issues',
        'Source' : 'https://github.com/fooof-tools/fooof'
    },
    download_url = 'https://github.com/fooof-tools/fooof/releases',
    keywords = ['neuroscience', 'neural oscillations', 'power spectra', '1/f', 'electrophysiology'],
    install_requires = install_requires,
    tests_require = ['pytest'],
    extras_require = {
        'plot'    : ['matplotlib'],
        'data'    : ['pandas'],
        'tests'   : ['pytest'],
        'all'     : ['matplotlib', 'pandas', 'tqdm', 'pytest']
    }
)
