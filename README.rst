=========================
Spectral Parameterization
=========================

|ProjectStatus| |Version| |BuildStatus| |Coverage| |License| |PythonVersions| |Publication|

.. |ProjectStatus| image:: https://www.repostatus.org/badges/latest/active.svg
   :target: https://www.repostatus.org/#active
   :alt: project status

.. |Version| image:: https://img.shields.io/pypi/v/fooof.svg
   :target: https://pypi.org/project/fooof/
   :alt: version

.. |BuildStatus| image:: https://github.com/fooof-tools/fooof/actions/workflows/build.yml/badge.svg
   :target: https://github.com/fooof-tools/fooof/actions/workflows/build.yml
   :alt: build status

.. |Coverage| image:: https://codecov.io/gh/fooof-tools/fooof/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/fooof-tools/fooof
   :alt: coverage

.. |License| image:: https://img.shields.io/pypi/l/fooof.svg
   :target: https://opensource.org/license/apache-2-0
   :alt: license

.. |PythonVersions| image:: https://img.shields.io/pypi/pyversions/fooof.svg
   :target: https://pypi.org/project/fooof/
   :alt: python versions

.. |Publication| image:: https://img.shields.io/badge/paper-nn10.1038-informational.svg
   :target: https://doi.org/10.1038/s41593-020-00744-x
   :alt: publication

Spectral parameterization (`specparam`, formerly `fooof`) is a fast, efficient, and physiologically-informed tool to parameterize neural power spectra.

WARNING: this Github repository has been updated to a major update / breaking change from previous releases, which were under the `fooof` name, and now contains major breaking update for the new `specparam` version of the code. The new version is not fully released, though a test version is available (see installation instructions below).

Overview
--------

The power spectrum model conceives of a model of the power spectrum as a combination of two distinct functional processes:

- An aperiodic component, reflecting 1/f like characteristics, with
- A variable number of periodic components (putative oscillations), as peaks rising above the aperiodic component

This model driven approach can be used to measure periodic and aperiodic properties of electrophysiological data,
including EEG, MEG, ECoG and LFP data.

The benefit of fitting a model in order to measure putative oscillations, is that peaks in the power spectrum are
characterized in terms of their specific center frequency, power and bandwidth without requiring predefining
specific bands of interest and controlling for the aperiodic component.
The model also returns a measure of this aperiodic components of the signal, allowing for measuring and
comparison of 1/f-like components of the signal within and between subjects.

specparam (upcoming version)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We are currently in the process of a major update to this tool, that includes a name changes (fooof -> specparam), and full rewrite of the code. This means that the new version will be incompatible with prior versions (in terms of the code having different names, and previous code no longer running as written), though note that the exact same procedures will be available (spectra can be fit in a way expected to give the same results), as well many new features.

The new version is called `specparam` (spectral parameterization). There is a release candidate available for testing (see installation instructions).

fooof (stable version)
~~~~~~~~~~~~~~~~~~~~~~

The fooof naming scheme, with most recent stable version 1.1 is the current main release, and is fully functional and stable, including everything that was introduced under the fooof name.

Which version should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The previous release version, fooof, is fully functional, and projects that are already using it might as well stick with that, unless any of the new functionality in specparam is particularly important. For projects that are just starting, the new specparam version may be of interest if some of the new features are of interest (e.g. time-resolved estimations), though note that as release candidates, the release are not guaranteed to be stable (future updates may make breaking changes). Note that for the same model and settings, fooof and specparam should be exactly equivalent, so in terms of outputs there should be no difference in choosing one or the other.

Documentation
-------------

The `specparam` package includes a full set of code documentation.

specparam (upcoming version)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To see the documentation for the candidate 2.0 release, see
`here <https://specparam-tools.github.io/>`_.

fooof (stable version)
~~~~~~~~~~~~~~~~~~~~~~

Documentation is available on the
`documentation site <https://fooof-tools.github.io/>`_.

This documentation includes:

- `Motivations <https://fooof-tools.github.io/fooof/auto_motivations/index.html>`_:
  with motivating examples of why we recommend parameterizing neural power spectra
- `Tutorials <https://fooof-tools.github.io/fooof/auto_tutorials/index.html>`_:
  with a step-by-step guide through the model and how to apply it
- `Examples <https://fooof-tools.github.io/fooof/auto_examples/index.html>`_:
  demonstrating example analyses and use cases, and other functionality
- `API list <https://fooof-tools.github.io/fooof/api.html>`_:
  which lists and describes all the code and functionality available in the module
- `FAQ <https://fooof-tools.github.io/fooof/faq.html>`_:
  answering frequency asked questions
- `Glossary <https://fooof-tools.github.io/fooof/glossary.html>`_:
  which defines all the key terms used in the module
- `Reference <https://fooof-tools.github.io/fooof/reference.html>`_:
  with information for how to reference and report on using the module

Dependencies
------------

`specparam` is written in Python, and requires Python >= 3.7 to run.

It has the following required dependencies:

- `numpy <https://github.com/numpy/numpy>`_
- `scipy <https://github.com/scipy/scipy>`_ >= 0.19

There are also optional dependencies, which are not required for model fitting itself, but offer extra functionality:

- `matplotlib <https://github.com/matplotlib/matplotlib>`_ is needed to visualize data and model fits
- `tqdm <https://github.com/tqdm/tqdm>`_ is needed to print progress bars when fitting many models
- `pandas <https://github.com/pandas-dev/pandas>`_ is needed for exporting model fit results to dataframes
- `pytest <https://github.com/pytest-dev/pytest>`_ is needed to run the test suite locally

Installation
------------

specparam / fooof can be installed using pip.

specparam (test version)
~~~~~~~~~~~~~~~~~~~~~~~~

To install the current release candidate version for the new 2.0 version, you can do:

.. code-block:: shell

    $ pip install specparam

The above will install the most recent release candidate.

NOTE: specparam is currently available as a 'release candidate', meaning it is not finalized and fully released yet.
This means it may not yet have all features that the ultimate 2.0 version will include, and things are not strictly
guaranteed to stay the same (there may be further breaking changes in the ultimate 2.0 release).

fooof (stable version)
~~~~~~~~~~~~~~~~~~~~~~

The current major release is the 1.X.X series, which is a breaking change from the prior 0.X.X series.

Check the `changelog <https://fooof-tools.github.io/fooof/changelog.html>`_ for notes on updating to the new version.

**Stable Version**

To install the latest stable release, use pip:

.. code-block:: shell

    $ pip install fooof

The module can also be installed with conda, from the conda-forge channel:

.. code-block:: shell

    $ conda install -c conda-forge fooof

**Development Version**

To get the current development version, first clone this repository:

.. code-block:: shell

    $ git clone https://github.com/fooof-tools/fooof

To install this cloned copy, move into the directory you just cloned, and run:

.. code-block:: shell

    $ pip install .

**Editable Version**

To install an editable version, download the development version as above, and run:

.. code-block:: shell

    $ pip install -e .

Other Language Support
----------------------

The original implementation of `specparam`, available in this repository, is implemented in Python.

If you wish to run specparam from another language, there are a couple potential options:

- a `wrapper`, which allows for running the Python code from another language
- a `reimplementation`, which reflects a new implementation of the specparam algorithm in another language

Below are listed some examples of wrappers and/or re-implementations in other languages (non-exhaustive).

Matlab
~~~~~~

In Matlab, there is a reimplementation available in common toolboxes:
- The `Brainstorm <https://neuroimage.usc.edu/brainstorm/Introduction>`_ toolbox has a reimplementation of specparam (see the `Brainstorm fooof tutorial <https://neuroimage.usc.edu/brainstorm/Tutorials/Fooof>`_)
- The `Fieldtrip <https://www.fieldtriptoolbox.org/>`_ toolbox also uses the same reimplementation (see the `Fieldtrip fooof tutorial <https://www.fieldtriptoolbox.org/example/fooof/>`_)

There is also a Matlab wrapper in the `fooof_mat <https://github.com/fooof-tools/fooof_mat>`_ repository.

Note that another option is to use Python FOOOF within a Matlab pipeline, as explored in the
`mat_py_mat <https://github.com/fooof-tools/mat_py_mat>`_ repository.

Other Languages
~~~~~~~~~~~~~~~

Other languages with wrappers include:

- Julia, for which there is a `fooof wrapper <https://juliahub.com/ui/Packages/PyFOOOF/Ng8hN/0.1.0>`_
- R, in which fooof can be run using `reticulate <https://rstudio.github.io/reticulate/>`_, as `shown here <https://github.com/fooof-tools/DevelopmentalDemo/tree/main/R>`_

Reference
---------

If you use this code in your project, please cite::

    Donoghue T, Haller M, Peterson EJ, Varma P, Sebastian P, Gao R, Noto T, Lara AH, Wallis JD,
    Knight RT, Shestyuk A, & Voytek B (2020). Parameterizing neural power spectra into periodic
    and aperiodic components. Nature Neuroscience, 23, 1655-1665.
    DOI: 10.1038/s41593-020-00744-x

Direct link: https://doi.org/10.1038/s41593-020-00744-x

More information for how to cite this method can be found on the
`reference page <https://fooof-tools.github.io/fooof/reference.html>`_.

Code and analyses from the paper are also available in the
`paper repository <https://github.com/fooof-tools/Paper>`_.

Contribute
----------

This project welcomes and encourages contributions from the community!

To file bug reports and/or ask questions about this project, please use the
`Github issue tracker <https://github.com/fooof-tools/fooof/issues>`_.

To see and get involved in discussions about the module, check out:

- the `issues board <https://github.com/fooof-tools/fooof/issues>`_ for topics relating to code updates, bugs, and fixes
- the `development page <https://github.com/fooof-tools/Development>`_ for discussion of potential major updates to the module

When interacting with this project, please use the
`contribution guidelines <https://github.com/fooof-tools/fooof/blob/main/CONTRIBUTING.md>`_
and follow the
`code of conduct <https://github.com/fooof-tools/fooof/blob/main/CODE_OF_CONDUCT.md>`_.

Quickstart
----------

This module is object oriented, and uses a similar approach as used in scikit-learn.

The algorithm works on frequency representations, that is power spectra in linear space.

**Fitting a Single Power Spectrum**

With a power spectrum loaded (with 'freqs' storing frequency values, and 'spectrum' storing
the power spectrum, both as 1D arrays in linear space) parameterization can be done as follows:

.. code-block:: python

    # Import the model object
    from specparam import SpectralModel

    # Initialize model object
    fm = SpectralModel()

    # Define frequency range across which to model the spectrum
    freq_range = [3, 40]

    # Parameterize the power spectrum, and print out a report
    fm.report(freqs, spectrum, freq_range)

SpectralModel.report() fits the model, plots the original power spectrum with the associated model fit,
and prints out the parameters of the model fit for both the aperiodic component, and parameters for
any identified peaks, reflecting periodic components.

Example output for the report of a parameterized fit on an individual power spectrum:

.. image:: https://raw.githubusercontent.com/fooof-tools/fooof/main/doc/img/FOOOF_report.png

**Defining the model Settings**

The settings for the algorithm are:

* ``peak_width_limits`` sets the possible lower- and upper-bounds for the fitted peak widths.
* ``max_n_peaks`` sets the maximum number of peaks to fit.
* ``min_peak_height`` sets an absolute limit on the minimum height (above aperiodic) for any extracted peak.
* ``peak_threshold`` sets a relative threshold above which a peak height must cross to be included in the model.
* ``aperiodic_mode`` defines the approach to use to parameterize the aperiodic component.

These settings can be defined when initializing the model, for example:

.. code-block:: python

    # Initialize a model object with defined settings
    fm = SpectralModel(peak_width_limits=[1.0, 8.0], max_n_peaks=6, min_peak_height=0.1,
                       peak_threshold=2.0, aperiodic_mode='fixed')

**Fitting a Group of Power Spectra**

Next is an example workflow for fitting a group of neural power spectra.
In this case, 'freqs' is again a 1D array of frequency values, and 'spectra' is a 2D array of power spectra.
We can fit the group of power spectra by doing:

.. code-block:: python

    # Initialize a SpectralGroupModel object, specifying some parameters
    fg = SpectralGroupModel(peak_width_limits=[1.0, 8.0], max_n_peaks=8)

    # Fit models across the matrix of power spectra
    fg.fit(freqs, spectra)

    # Create and save out a report summarizing the results across the group of power spectra
    fg.save_report()

    # Save out results for further analysis later
    fg.save(file_name='group_results', save_results=True)

Example output from using SpectralGroupModel across a group of power spectra:

.. image:: https://raw.githubusercontent.com/fooof-tools/fooof/main/doc/img/FOOOFGroup_report.png

**Other Functionality**

The module also includes functionality for fitting the model to matrices of multiple power spectra,
saving and loading results, creating reports describing model fits, analyzing model outputs,
plotting models and parameters, and simulating power spectra, all of which is described in the
`documentation <https://fooof-tools.github.io/fooof/>`_.

Funding
-------

Supported by NIH award R01 GM134363 from the
`NIGMS <https://www.nigms.nih.gov/>`_.

.. image:: https://www.nih.gov/sites/all/themes/nih/images/nih-logo-color.png
  :width: 400

|
