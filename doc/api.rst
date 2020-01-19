.. _api_documentation:

=================
API Documentation
=================

This is the API reference for the FOOOF module.

Table of Contents
=================

.. contents::
   :local:
   :depth: 2

.. currentmodule:: fooof

FOOOF Objects
-------------

FOOOF objects that handle data and fit models to parameterize neural power spectra.

Base FOOOF Object
~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   FOOOF

FOOOFGroup Object
~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   FOOOFGroup

FOOOF Functions
---------------

Functions to manipulate, examine and analyze FOOOF objects, and related utilities.

Manage FOOOF Objects
~~~~~~~~~~~~~~~~~~~~

Functions to manage and manipulate FOOOF objects.

.. currentmodule:: fooof.funcs

.. autosummary::
   :toctree: generated/

   average_fg
   combine_fooofs
   fit_fooof_group_3d

Check FOOOF Objects
~~~~~~~~~~~~~~~~~~~

Functions to help examine and audit FOOOF objects.

.. currentmodule:: fooof.checks

.. autosummary::
    :toctree: generated/

    get_info
    compare_info
    compute_pointwise_error_fm
    compute_pointwise_error_fg

Analyze FOOOF Object Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions to help analyze FOOOF results.

.. currentmodule:: fooof.analysis

.. autosummary::
    :toctree: generated/

    get_band_peak
    get_band_peak_group
    get_band_peak_fm
    get_band_peak_fg
    get_highest_peak

Simulation Code
---------------

Code & utilities for simulating power spectra.

Generate Power Spectra
~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.sim.gen

.. autosummary::
    :toctree: generated/

    gen_freqs
    gen_power_spectrum
    gen_group_power_spectra

Manage Parameters
~~~~~~~~~~~~~~~~~

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

.. currentmodule:: fooof.sim.transform

.. autosummary::
    :toctree: generated/

    translate_spectrum
    translate_sim_spectrum
    rotate_spectrum
    rotate_sim_spectrum
    compute_rotation_offset

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
    plot_spectrum_error

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

Plot from FOOOF Object
~~~~~~~~~~~~~~~~~~~~~~

Plots for visualizing from FOOOF objects.

.. currentmodule:: fooof.plts.fm

.. autosummary::
    :toctree: generated/

    plot_fm
    plot_fm_peak_iter

.. currentmodule:: fooof.plts.fg

.. autosummary::
    :toctree: generated/

    plot_fg

Utilities
---------

Utility functions and objects.

Manage Oscillation Bands
~~~~~~~~~~~~~~~~~~~~~~~~

Object to handle oscillation band definitions.

.. currentmodule:: fooof.bands

.. autosummary::
   :toctree: generated/

   Bands

General Utilities
~~~~~~~~~~~~~~~~~

General utility functions.

.. currentmodule:: fooof.utils

.. autosummary::
    :toctree: generated/

    trim_spectrum
    compute_pointwise_error
