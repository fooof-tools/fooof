Reference and Reporting Information
===================================

This page covers information for how to reference and report on using FOOOF, as well as some collected
informaiton and examples of projects, tools, and analyses that have and can be done using FOOOF.

Table of Contents
-----------------
.. contents::
   :local:
   :backlinks: none

Reference
~~~~~~~~~

The reference for this method is
`Parameterizing Neural Power Spectra <https://doi.org/10.1101/299859>`_.

This link currently leads to a preprint, on biorxiv. The paper is currently under review,
and this link will be updated to the accepted journal version when available.

The paper reports on the method, and include simulation work and example analyses and applications.
The code for the simulations and applications is all indexed and available
`here <https://github.com/fooof-tools/Paper>`_.

Please cite this paper if you use this method, and/or if you wish to refer to the our approach for parameterizing neural power spectra, and/or to refer to any ideas and examples from this website.

Example Applications
~~~~~~~~~~~~~~~~~~~~

You can find the full list of articles that cite the `Parameterizing Neural Power Spectra` paper
`here <https://scholar.google.com/scholar?oi=bibs&hl=en&cites=1591416229268020768,15214833138798132105,12543969463602123647>`_
(this links to Google scholar).

Methods Reporting
~~~~~~~~~~~~~~~~~

If you wish to report that you used FOOOF, we recommend including the following information in the methods section:

- The version of FOOOF used (for example 1.0.0)
- The algorithm settings that were used

  - You should report all public settings, even if default values are used
- The frequency range of the data that was fit

In addition, we recommend that reports should include information on:

- Details of the data, including modality and any pre-processing steps applied
- How power spectrum were generated, including the length of segments used to calculate spectra
- If and how model goodness-of-fit measures were assessed

Reporting Template & Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An example methods report might look like:

    The FOOOF algorithm (version *X.X.X*) was used to parameterize neural power spectra. Settings for the
    algorithm were set as: peak width limits : *XX*; max number of peaks : *XX*; minimum peak height : *XX*;
    peak threshold : *XX*; and aperiodic mode : *XX*. Power spectra were parameterized across
    the frequency range *XX* to *XX* Hz.

Where all of the *X*'s should be filled in with the relevant information.

Note that as of FOOOF version 1.0.0 there is code utility that will generate this information for you.
If you have a FOOOF object defined (such as `FOOOF` or `FOOOFGroup`), as 'fooof_obj', you
can run the following code to print out the information you need and/or a template of the
methods report:

.. code-block:: python

    # Print out all the methods information for reporting
    methods_report_info(fooof_obj)

    # Generate methods text, with methods information inserted
    methods_report_text(fooof_obj)
