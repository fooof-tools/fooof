Reference and Reporting Information
===================================

This page describes how to reference and report on using this method for parameterizing neural power spectra, and related information.

Table of Contents
-----------------
.. contents::
   :local:
   :backlinks: none

Reference
~~~~~~~~~

If you use this method, and/or want to refer to our approach, examples, and discussion points, please cite the following paper:

.. topic:: Reference

    Donoghue T, Haller M, Peterson EJ, Varma P, Sebastian P, Gao R, Noto T, Lara AH, Wallis JD,
    Knight RT, Shestyuk A, Voytek B (2020). Parameterizing neural power spectra into periodic and aperiodic
    components. Nature Neuroscience, 23, 1655-1665. DOI: 10.1038/s41593-020-00744-x

Direct link: https://doi.org/10.1038/s41593-020-00744-x

Example Applications
~~~~~~~~~~~~~~~~~~~~

As well as reporting on the method, the full version of the paper includes simulation work as well as example analyses and applications.
The code for the simulations and applications is indexed and available in the
`Paper repository <https://github.com/fooof-tools/Paper>`_.

You can also find the full list of articles that cite the `Parameterizing Neural Power Spectra` paper at this
`Google scholar link <https://scholar.google.com/scholar?oi=bibs&hl=en&cites=1591416229268020768,15214833138798132105,12543969463602123647>`_.

Methods Reporting
~~~~~~~~~~~~~~~~~

If you use this module and the power spectrum model in your work, there is some information you should include in the methods section.

Specifically, we recommend including the following information in the methods section:

- The version number of the module that was used (for example 1.0.0)
- The algorithm settings that were used

  - You should report all public settings, even if default values are used
- The frequency range of the data that was fit

In addition, we recommend that reports should include information on:

- Details of the data, including modality and any preprocessing steps applied
- How power spectrum were generated, including the length of segments used to calculate spectra
- If and how model goodness-of-fit measures were assessed

Reporting Template & Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To assist in reporting on using FOOOF, we have created some templates for reporting on spectral parameterization methods. There are also some utilities included in the code to collected the required information. 

The following box is an example of what a methods report might look like (where all of the *X*'s should be filled in with the relevant information).

.. topic:: Methods Report Template

    The FOOOF algorithm (version *X.X.X*) was used to parameterize neural power spectra. Settings for the
    algorithm were set as: peak width limits : *XX*; max number of peaks : *XX*; minimum peak height : *XX*;
    peak threshold : *XX*; and aperiodic mode : *XX*. Power spectra were parameterized across
    the frequency range *XX* to *XX* Hz.

Generating Methods Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~

As of FOOOF version 1.0.0 there are code utilities to extract all required information for reporting, and for generating methods reports.

These utilities require a defined FOOOF object, such as `FOOOF` or `FOOOFGroup`, assumed to be called 'fooof_obj' in the following examples. This object will be used to extract all the relevant settings and any available meta-data for reporting.

The :func:`~fooof.utils.reports.methods_report_info` function can be used to print out the information you need for reporting:

.. code-block:: python

    # Import the utility to print out information for reporting
    from fooof.utils.reports import methods_report_info

    # Print out all the methods information for reporting
    methods_report_info(fooof_obj)

The :func:`~fooof.utils.reports.methods_report_text` function can be used to print out an auto-generated methods report, like the one demonstrated above, with all available information filled:

.. code-block:: python

    # Import the utility to print out information for reporting
    from fooof.utils.reports import methods_report_text

    # Generate methods text, with methods information inserted
    methods_report_text(fooof_obj)
