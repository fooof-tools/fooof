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

Model Object
~~~~~~~~~~~~

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

.. currentmodule:: specparam.models

.. autosummary::
   :toctree: generated/

   compare_model_objs
   combine_model_objs
   average_group
   average_reconstructions
   fit_models_3d

Component Objects
-----------------

The model object combines multiple sub-objects that define and store different
elements of the model definition, data, and results.

Here, the main sub-objects are listed, some of which can also be used independently.

Bands
~~~~~

An object for defining frequency band definitions.

.. currentmodule:: specparam

.. autosummary::
   :toctree: generated/

   Bands

Algorithm
~~~~~~~~~

An object for defining fit algorithms.

.. currentmodule:: specparam.algorithms.algorithm

.. autosummary::
   :toctree: generated/

   Algorithm

Modes
~~~~~

An object for defining fit modes.

.. currentmodule:: specparam.modes.mode

.. autosummary::
   :toctree: generated/

   Mode

Associated objects allow for defining mode parameters.

.. currentmodule:: specparam.modes.params

.. autosummary::
   :toctree: generated/

   ParamDefinition

Utility to check for available fit modes.

.. currentmodule:: specparam.modes.definitions

.. autosummary::
   :toctree: generated/

   check_modes

Metrics
~~~~~~~

An object for defining metrics.

.. currentmodule:: specparam.metrics.metric

.. autosummary::
   :toctree: generated/

   Metric

Utility to check for available metrics.

.. currentmodule:: specparam.metrics.definitions

.. autosummary::
   :toctree: generated/

   check_metrics

Data
~~~~

An object for managing data to be modeled.

.. currentmodule:: specparam.data.data

.. autosummary::
   :toctree: generated/

   Data

Results
~~~~~~~

An object for managing model results.

.. currentmodule:: specparam.results.results

.. autosummary::
   :toctree: generated/

   Results

Data Objects
------------

Objects to manage model information, and simulation parameters.

Model Information
~~~~~~~~~~~~~~~~~

Objects to store settings, metadata and results for power spectrum models.

.. currentmodule:: specparam.data

.. autosummary::
   :toctree: generated/
   :template: data_object.rst

   SpectrumMetaData
   ModelModes
   ModelSettings
   ModelChecks
   FitResults

Simulation Parameters
~~~~~~~~~~~~~~~~~~~~~

Object to store information about simulated data.

.. autosummary::
   :toctree: generated/
   :template: data_object.rst

   SimParams

Periodic Components
~~~~~~~~~~~~~~~~~~~

Functions for accessing the periodic components of model fits.

**Object Inputs**

The following functions take in model objects directly, which is the typical use case.

.. currentmodule:: specparam.data.periodic

.. autosummary::
    :toctree: generated/

    get_band_peak
    get_band_peak_group
    get_band_peak_event

**Array Inputs**

The following functions operate on arrays of peak parameters, which may be useful for more custom work-flows.

.. currentmodule:: specparam.data.periodic

.. autosummary::
    :toctree: generated/

    get_band_peak_arr
    get_band_peak_group_arr
    get_highest_peak
    threshold_peaks
    sort_peaks

Measures
--------

Functionality to analyze power spectrum models and the results parameters / components.

Model Errors
~~~~~~~~~~~~

Functions for analyzing the error of model fits.

**Object Inputs**

The following functions take in model objects directly.

.. currentmodule:: specparam.measures.pointwise

.. autosummary::
    :toctree: generated/

    compute_pointwise_error
    compute_pointwise_error_group

**Array Inputs**

The following functions operate on arrays of models and data, which may be useful for more custom work-flows.

.. currentmodule:: specparam.measures.pointwise

.. autosummary::
    :toctree: generated/

    compute_pointwise_error_arr

Parameters
~~~~~~~~~~

Measures & utilities for working with and converting parameters.

.. currentmodule:: specparam.measures.params

.. autosummary::
    :toctree: generated/

    compute_knee_frequency
    compute_time_constant

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

.. currentmodule:: specparam.plts.style

.. autosummary::
    :toctree: generated/

    check_style_options

.. currentmodule:: specparam.plts.utils

.. autosummary::
    :toctree: generated/

    check_ax
    recursive_plot
    save_figure

Input / Output (IO)
-------------------

Save & load related functionality.

.. currentmodule:: specparam.io.models

.. autosummary::
    :toctree: generated/

    save_model
    save_group
    save_event
    load_model
    load_group
    load_time
    load_event

Reports
-------

Utilities related to creating reports.

Methods Reports
~~~~~~~~~~~~~~~

Utilities for creating draft methods sections.

.. currentmodule:: specparam.reports.methods

.. autosummary::
    :toctree: generated/

    methods_report_info
    methods_report_text

Utilities
---------

Utility functions and objects.

Spectral Utilities
~~~~~~~~~~~~~~~~~~

Utilities for working with spectral data.

.. currentmodule:: specparam.utils.spectral

.. autosummary::
    :toctree: generated/

    trim_spectrum
    interpolate_spectrum
    interpolate_spectra
    subsample_spectra

Array Utilities
~~~~~~~~~~~~~~~

Utilities that can be applied to arrays.

.. currentmodule:: specparam.utils.array

.. autosummary::
    :toctree: generated/

    normalize
    unlog
    compute_arr_desc
