.. _api_documentation:

=================
API Documentation
=================

API reference for the FOOOF module.

Table of Contents
=================

.. contents::
   :local:
   :depth: 2

.. currentmodule:: fooof

FOOOF Objects
-------------

Objects that manage data and fit models to parameterize neural power spectra.

FOOOF Object
~~~~~~~~~~~~

The FOOOF object is the base object for the model, and can be used to fit individual power spectra.

.. autosummary::
   :toctree: generated/

   FOOOF

FOOOFGroup Object
~~~~~~~~~~~~~~~~~

The FOOOFGroup object allows for parameterizing groups of power spectra.

.. autosummary::
   :toctree: generated/

   FOOOFGroup

Object Utilities
~~~~~~~~~~~~~~~~

Functions to manipulate, examine and analyze FOOOF objects, and related utilities.

.. currentmodule:: fooof.objs.utils

.. autosummary::
   :toctree: generated/

   compare_info
   average_fg
   combine_fooofs
   fit_fooof_3d

Bands Object
------------

An object to handle oscillation band definitions.

.. currentmodule:: fooof.bands.bands

.. autosummary::
   :toctree: generated/

   Bands

Data Objects
------------

Objects to manage and store data.

Model Information
~~~~~~~~~~~~~~~~~

Objects to store settings, metadata and results for FOOOF models.

.. currentmodule:: fooof.data

.. autosummary::
   :toctree: generated/
   :template: data_object.rst

   FOOOFSettings
   FOOOFMetaData
   FOOOFResults

Simulation Parameters
~~~~~~~~~~~~~~~~~~~~~

Object to store information about simulated data.

.. autosummary::
   :toctree: generated/
   :template: data_object.rst

   SimParams

Analyze Model Results
---------------------

Functions to analyze FOOOF results.

Analyze Model Errors
~~~~~~~~~~~~~~~~~~~~

Functions for analyzing the error of model fits.

.. currentmodule:: fooof.analysis.error

.. autosummary::
    :toctree: generated/

    compute_pointwise_error_fm
    compute_pointwise_error_fg

Analyze Periodic Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for analyzing the periodic components of model fits.

.. currentmodule:: fooof.analysis.periodic

The following functions take in FOOOF objects directly, which is the typical use case:

.. autosummary::
    :toctree: generated/

    get_band_peak_fm
    get_band_peak_fg

The following functions operate on arrays of peak parameters, which may be useful for more custom workflows:

.. autosummary::
    :toctree: generated/

    get_band_peak
    get_band_peak_group
    get_highest_peak
    threshold_peaks

Simulation Code
---------------

Code & utilities for simulating power spectra.

Generate Power Spectra
~~~~~~~~~~~~~~~~~~~~~~

Functions for simulating neural power spectra.

.. currentmodule:: fooof.sim.gen

.. autosummary::
    :toctree: generated/

    gen_freqs
    gen_power_spectrum
    gen_group_power_spectra

Manage Parameters
~~~~~~~~~~~~~~~~~

Functions and objects for managing parameters for simulated power spectra.

.. currentmodule:: fooof.sim.params

.. autosummary::
    :toctree: generated/

    Stepper
    param_iter
    param_sampler
    param_jitter
    update_sim_ap_params

Transform Power Spectra
~~~~~~~~~~~~~~~~~~~~~~~

Functions for transforming power spectra.

.. currentmodule:: fooof.sim.transform

.. autosummary::
    :toctree: generated/

    translate_spectrum
    translate_sim_spectrum
    rotate_spectrum
    rotate_sim_spectrum
    compute_rotation_offset
    compute_rotation_frequency

Utilities
~~~~~~~~~

Utilities for simulating power spectra.

.. currentmodule:: fooof.sim.utils

.. autosummary::
    :toctree: generated/

    set_random_seed

Plotting Functions
------------------

Visualizations.

Plot Power Spectra
~~~~~~~~~~~~~~~~~~

Plots for visualizing power spectra.

.. currentmodule:: fooof.plts.spectra

.. autosummary::
    :toctree: generated/

    plot_spectrum
    plot_spectra
    plot_spectrum_shading
    plot_spectra_shading
    plot_spectral_error

Plot Parameters
~~~~~~~~~~~~~~~

Plots for visualizing model parameters and components.

.. currentmodule:: fooof.plts.aperiodic

.. autosummary::
    :toctree: generated/

    plot_aperiodic_fits
    plot_aperiodic_params

.. currentmodule:: fooof.plts.periodic

.. autosummary::
    :toctree: generated/

    plot_peak_fits
    plot_peak_params

Plot FOOOF Objects
~~~~~~~~~~~~~~~~~~

Plots for visualizing model from FOOOF objects.

.. currentmodule:: fooof.plts.fm

.. autosummary::
    :toctree: generated/

    plot_fm

.. currentmodule:: fooof.plts.fg

.. autosummary::
    :toctree: generated/

    plot_fg

Annotated Plots
~~~~~~~~~~~~~~~

Annotated plots that describe the model and fitting process.

.. currentmodule:: fooof.plts.annotate

.. autosummary::
    :toctree: generated/

    plot_annotated_model
    plot_annotated_peak_search

Utilities
---------

Utility functions and objects.

Input / Output (IO)
~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.utils.io

.. autosummary::
    :toctree: generated/

    load_fooof
    load_fooofgroup

Parameter Utilities
~~~~~~~~~~~~~~~~~~~

Utilities for working with parameters

.. currentmodule:: fooof.utils.params

.. autosummary::
    :toctree: generated/

    compute_knee_frequency

Data Utilities
~~~~~~~~~~~~~~

Utilities for working with data.

.. currentmodule:: fooof.utils.data

.. autosummary::
    :toctree: generated/

    trim_spectrum
    interpolate_spectrum
    compute_pointwise_error

Reports
~~~~~~~

Utilities to create reports.

.. currentmodule:: fooof.utils.reports

.. autosummary::
    :toctree: generated/

    methods_report_info
    methods_report_text
