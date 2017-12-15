"""FOOOF setup script."""

from setuptools import setup, find_packages

# Get the current version number from inside the module
with open(os.path.join('fooof', 'version.py')) as vf:
    exec(vf.read())

setup(
    name = 'fooof',
    version = __version__,
    description = 'Fitting oscillations & one-over f',
    author = 'The Voytek Lab',
    author_email = 'voyteklab@gmail.com',
    url = 'https://github.com/voytekresearch/fooof',
    packages=find_packages(),
    license='Apache License, 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
    download_url = '',
    keywords = ['neuroscience', 'neural oscillations', 'power spectra', '1/f', 'electrophysiology'],
    install_requires=['numpy', 'scipy>=0.19.0']
)