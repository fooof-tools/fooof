"""FOOOF setup script."""

from setuptools import setup, find_packages

setup(
    name = 'fooof',
    version = '0.1.0',
    description = 'Fitting oscillations & one-over f',
    author = 'The Voytek Lab',
    author_email = 'voyteklab@gmail.com',
    url = 'https://github.com/voytekresearch/fooof',
    packages=find_packages(),
    license='MIT',
    download_url = '',
    keywords = ['neuroscience', 'neural oscillations', 'power spectra', '1/f', 'electrophysiology'],
    classifiers = []
)