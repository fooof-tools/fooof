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

Model Objects
-------------

Objects that manage data and fit the model to parameterize neural power spectra.

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

.. currentmodule:: fooof.objs

.. autosummary::
   :toctree: generated/

   compare_info
   average_fg
   combine_fooofs

.. currentmodule:: fooof

.. autosummary::
   :toctree: generated/

   fit_fooof_3d

Data Objects
------------

Objects to manage frequency bands, model information, and simulation parameters.

Bands Object
~~~~~~~~~~~~

An object to handle frequency band definitions.

.. currentmodule:: fooof

.. autosummary::
   :toctree: generated/

   Bands

Model Information
~~~~~~~~~~~~~~~~~

Objects to store settings, metadata and results for power spectrum models.

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

Functions to analyze power spectrum models and the results parameters / components.

Analyze Model Errors
~~~~~~~~~~~~~~~~~~~~

Functions for analyzing the error of model fits.

**Object Inputs**

The following functions take in FOOOF objects directly, which is the recommended approach.

.. currentmodule:: fooof.analysis

.. autosummary::
    :toctree: generated/

    compute_pointwise_error_fm
    compute_pointwise_error_fg

**Array Inputs**

The following functions operate on arrays of models and data, which may be useful for more custom work-flows.

.. currentmodule:: fooof.analysis.error

.. autosummary::
    :toctree: generated/

    compute_pointwise_error

Analyze Periodic Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for analyzing the periodic components of model fits.

**Object Inputs**

The following functions take in FOOOF objects directly, which is the typical use case.

.. currentmodule:: fooof.analysis

.. autosummary::
    :toctree: generated/

    get_band_peak_fm
    get_band_peak_fg

**Array Inputs**

The following functions operate on arrays of peak parameters, which may be useful for more custom work-flows.

.. currentmodule:: fooof.analysis.periodic

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

.. currentmodule:: fooof.sim

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

Simulation Utilities
~~~~~~~~~~~~~~~~~~~~

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

.. currentmodule:: fooof.plts

.. autosummary::
    :toctree: generated/

    plot_spectra

Plots for plotting power spectra with shaded regions.

.. currentmodule:: fooof.plts.spectra

.. autosummary::
    :toctree: generated/

    plot_spectra_shading
    plot_spectra_yshade

Plot Model Properties & Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plots for visualizing **periodic** parameters and model components.

.. currentmodule:: fooof.plts.periodic

.. autosummary::
    :toctree: generated/

    plot_peak_fits
    plot_peak_params

Plots for visualizing **aperiodic** parameters and model components.

.. currentmodule:: fooof.plts.aperiodic

.. autosummary::
    :toctree: generated/

    plot_aperiodic_fits
    plot_aperiodic_params

Plots for visualizing model error.

.. currentmodule:: fooof.plts.error

.. autosummary::
    :toctree: generated/

    plot_spectral_error

Plot FOOOF Objects
~~~~~~~~~~~~~~~~~~

Plots for visualizing models from FOOOF objects.
Note that these are the same plotting functions that can be called from FOOOF objects directly.

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

Data Utilities
~~~~~~~~~~~~~~

Utilities for working with data.

.. currentmodule:: fooof.utils

.. autosummary::
    :toctree: generated/

    trim_spectrum
    interpolate_spectrum
    subsample_spectra

Parameter Utilities
~~~~~~~~~~~~~~~~~~~

Utilities for working with parameters

.. currentmodule:: fooof.utils.params

.. autosummary::
    :toctree: generated/

    compute_knee_frequency

Input / Output (IO)
~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.utils.io

.. autosummary::
    :toctree: generated/

    load_fooof
    load_fooofgroup

Methods Reports
~~~~~~~~~~~~~~~

Utilities to creating methods reports.

.. currentmodule:: fooof.utils.reports

.. autosummary::
    :toctree: generated/

    methods_report_info
    methods_report_text
