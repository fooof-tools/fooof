Reference and Reporting Information
===================================

This page describes how to reference and report the use of `specparam`, and related information.

Table of Contents
-----------------
.. contents::
   :local:
   :backlinks: none

Main Reference
~~~~~~~~~~~~~~

If you use this method, and/or want to refer to our approach, examples, and discussion points,
please cite the following paper:

.. topic:: Reference

    Donoghue T, Haller M, Peterson EJ, Varma P, Sebastian P, Gao R, Noto T, Lara AH, Wallis JD,
    Knight RT, Shestyuk A, Voytek B (2020). Parameterizing neural power spectra into periodic and aperiodic
    components. Nature Neuroscience, 23, 1655-1665. DOI: 10.1038/s41593-020-00744-x

Direct link: https://doi.org/10.1038/s41593-020-00744-x

Note beyond describing the method, this paper also includes simulations to evaluate performance
and example analyses and applications, the code for which is also available in the
`paper repository <https://github.com/fooof-tools/Paper>`_.

To explore the list of articles that cite this paper, you can use this
`Google scholar link <https://scholar.google.com/scholar?cites=1871208307712966933&as_sdt=5,33&sciodt=0,33&hl=en>`_.

Methods Reporting
~~~~~~~~~~~~~~~~~

If you use spectral parameterization to model power spectrum, there is some information
you should include in the methods section to describe this process, including:

- The version of the module that was used (for example 1.0.0)
- The frequency range of the data that was fit
- The fit modes and algorithm settings that were used (inclusive of all public settings,
  even if default values are used)
- Any additional processes used to update parameter estimates and/or to estimate other values from
  the power spectra and/or model components (e.g. if a computing power for particular band ranges)

In addition, we recommend that reports should include information on:

- Details of the data, including modality and any preprocessing steps applied
- How power spectrum were generated, including the length of segments used to calculate spectra
- If and how model goodness-of-fit measures were assessed

Reporting Template & Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module includes templates for reporting on the use of spectral parameterization methods,
with code utilities to collect the required information.

The following box is an example of what a methods report might look like (where all of the
*X*'s should be filled in with the relevant information).

.. topic:: Methods Report Template

    Power spectra were parameterized with the specparam Python tool (version *X.X.X*; Donoghue et al, 2020).
    Power spectra were modeled across the frequency range of *XX* to *XX* Hz, using a powerlaw aperiodic
    component and Gaussian periodic components, with the standard fitting approach, using algorithm settings
    of peak width limits : *XX*; max number of peaks : *XX*; minimum peak height : *XX*; peak threshold : *XX*;
    and aperiodic mode : *XX*. Goodness-of-fit measures were evaluated by XX.

Checking module version
~~~~~~~~~~~~~~~~~~~~~~~

If you are not sure which version of the module you have installed, you can
check the `__version__` from Python, using the following code:

.. code-block:: python

    # Check the version of the tool
    from specparam import __version__ as specparam_version
    print('Current specparam version:', specparam_version)

Generating Methods Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~

As of version 1.0.0 there are code utilities to extract all required information for reporting,
and for generating methods reports. These utilities require an initialized model object
(e.g. `SpectralModel`), labeled as 'model_obj' in these examples. This object will be used to
extract all the relevant settings and any available meta-data for reporting.

The :func:`~specparam.utils.reports.methods_report_info` function can be used to print out
the information you need for reporting:

.. code-block:: python

    # Import the utility to print out information for reporting
    from specparam.utils.reports import methods_report_info

    # Print out all the methods information for reporting
    methods_report_info(model_obj)

The :func:`~specparam.utils.reports.methods_report_text` function can be used to
print out an auto-generated methods report, like the one demonstrated above,
with all available information filled:

.. code-block:: python

    # Import the utility to print out information for reporting
    from specparam.utils.reports import methods_report_text

    # Generate methods text, with methods information inserted
    methods_report_text(model_obj)
