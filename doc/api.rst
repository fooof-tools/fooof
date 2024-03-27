.. _api_documentation:

=================
API Documentation
=================

API reference for the module.

Table of Contents
=================

.. contents::
   :local:
   :depth: 2

.. currentmodule:: specparam

Model Objects
-------------

Objects that manage data and fit the model to parameterize neural power spectra.

Base Object
~~~~~~~~~~~

The SpectralModel object is the base object for the model, and can be used to fit individual power spectra.

.. autosummary::
   :toctree: generated/

   SpectralModel

Group Object
~~~~~~~~~~~~

The SpectralGroupModel object allows for parameterizing groups of power spectra.

.. autosummary::
   :toctree: generated/

   SpectralGroupModel

Time & Event Objects
~~~~~~~~~~~~~~~~~~~~

The time & event objects allows for parameterizing power spectra organized across time and/or events.

.. autosummary::
   :toctree: generated/

   SpectralTimeModel
   SpectralTimeEventModel

Object Utilities
~~~~~~~~~~~~~~~~

Functions to manipulate, examine, and analyze model objects.

.. currentmodule:: specparam.objs

.. autosummary::
   :toctree: generated/

   compare_model_objs
   combine_model_objs
   average_group
   average_reconstructions

.. currentmodule:: specparam

.. autosummary::
   :toctree: generated/

   fit_models_3d

Data Objects
------------

Objects to manage frequency bands, model information, and simulation parameters.

Bands Object
~~~~~~~~~~~~

An object to handle frequency band definitions.

.. currentmodule:: specparam

.. autosummary::
   :toctree: generated/

   Bands

Model Information
~~~~~~~~~~~~~~~~~

Objects to store settings, metadata and results for power spectrum models.

.. currentmodule:: specparam.data

.. autosummary::
   :toctree: generated/
   :template: data_object.rst

   SpectrumMetaData
   ModelSettings
   ModelRunModes
   FitResults

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

The following functions take in model objects directly.

.. currentmodule:: specparam.analysis

.. autosummary::
    :toctree: generated/

    compute_pointwise_error
    compute_pointwise_error_group

**Array Inputs**

The following functions operate on arrays of models and data, which may be useful for more custom work-flows.

.. currentmodule:: specparam.analysis.error

.. autosummary::
    :toctree: generated/

    compute_pointwise_error_arr

Analyze Periodic Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for analyzing the periodic components of model fits.

**Object Inputs**

The following functions take in model objects directly, which is the typical use case.

.. currentmodule:: specparam.analysis

.. autosummary::
    :toctree: generated/

    get_band_peak
    get_band_peak_group
    get_band_peak_event

**Array Inputs**

The following functions operate on arrays of peak parameters, which may be useful for more custom work-flows.

.. currentmodule:: specparam.analysis.periodic

.. autosummary::
    :toctree: generated/

    get_band_peak_arr
    get_band_peak_group_arr
    get_highest_peak
    threshold_peaks

Simulation Code
---------------

Code & utilities for simulating power spectra.

Generate Power Spectra
~~~~~~~~~~~~~~~~~~~~~~

Functions for simulating neural power spectra and spectrograms.

.. currentmodule:: specparam.sim

.. autosummary::
    :toctree: generated/

    sim_power_spectrum
    sim_group_power_spectra
    sim_spectrogram

Manage Parameters
~~~~~~~~~~~~~~~~~

Functions and objects for managing parameters for simulated power spectra.

.. currentmodule:: specparam.sim.params

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

.. currentmodule:: specparam.sim.transform

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

.. currentmodule:: specparam.sim.utils

.. autosummary::
    :toctree: generated/

    create_freqs
    set_random_seed

Plotting Functions
------------------

Visualizations.

Plot Power Spectra
~~~~~~~~~~~~~~~~~~

Plots for visualizing power spectra and spectrograms.

.. currentmodule:: specparam.plts

.. autosummary::
    :toctree: generated/

    plot_spectra
    plot_spectrogram

Plots for plotting power spectra with shaded regions.

.. currentmodule:: specparam.plts.spectra

.. autosummary::
    :toctree: generated/

    plot_spectra_shading
    plot_spectra_yshade

Plot Model Properties & Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plots for visualizing **periodic** parameters and model components.

.. currentmodule:: specparam.plts.periodic

.. autosummary::
    :toctree: generated/

    plot_peak_fits
    plot_peak_params

Plots for visualizing **aperiodic** parameters and model components.

.. currentmodule:: specparam.plts.aperiodic

.. autosummary::
    :toctree: generated/

    plot_aperiodic_fits
    plot_aperiodic_params

Plots for visualizing model error.

.. currentmodule:: specparam.plts.error

.. autosummary::
    :toctree: generated/

    plot_spectral_error

Plot Model Objects
~~~~~~~~~~~~~~~~~~

Plots for visualizing from model objects.
Note that these are the same plotting functions that can be called from the model objects directly.

.. currentmodule:: specparam.plts.model

.. autosummary::
    :toctree: generated/

    plot_model

.. currentmodule:: specparam.plts.group

.. autosummary::
    :toctree: generated/

    plot_group_model

.. currentmodule:: specparam.plts.time

.. autosummary::
    :toctree: generated/

    plot_time_model

.. currentmodule:: specparam.plts.event

.. autosummary::
    :toctree: generated/

    plot_event_model

Annotated Plots
~~~~~~~~~~~~~~~

Annotated plots that describe the model and fitting process.

.. currentmodule:: specparam.plts.annotate

.. autosummary::
    :toctree: generated/

    plot_annotated_model
    plot_annotated_peak_search

Plot Utilities & Styling
~~~~~~~~~~~~~~~~~~~~~~~~

Plot related utilies for styling and managing plots.

.. currentmodule:: fooof.plts.style

.. autosummary::
    :toctree: generated/

    check_style_options

.. currentmodule:: fooof.plts.utils

.. autosummary::
    :toctree: generated/

    check_ax
    recursive_plot
    save_figure

Utilities
---------

Utility functions and objects.

Data Utilities
~~~~~~~~~~~~~~

Utilities for working with data.

.. currentmodule:: specparam.utils

.. autosummary::
    :toctree: generated/

    trim_spectrum
    interpolate_spectrum
    interpolate_spectra
    subsample_spectra

Parameter Utilities
~~~~~~~~~~~~~~~~~~~

Utilities for working with parameters

.. currentmodule:: specparam.utils.params

.. autosummary::
    :toctree: generated/

    compute_knee_frequency

Input / Output (IO)
~~~~~~~~~~~~~~~~~~~

.. currentmodule:: specparam.utils.io

.. autosummary::
    :toctree: generated/

    load_model
    load_group_model
    load_time_model
    load_event_model

Methods Reports
~~~~~~~~~~~~~~~

Utilities to creating methods reports.

.. currentmodule:: specparam.utils.reports

.. autosummary::
    :toctree: generated/

    methods_report_info
    methods_report_text
