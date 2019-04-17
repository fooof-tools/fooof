.. _api_documentation:

=================
API Documentation
=================

This is the API reference for classes & functions in the FOOOF module.

Table of Contents
=================

.. contents::
   :local:
   :depth: 2

.. currentmodule:: fooof

FOOOF Object
------------

.. autosummary::
   :toctree: generated/

   FOOOF

FOOOFGroup Object
-----------------

.. autosummary::
   :toctree: generated/

   FOOOFGroup

Bands
-----

.. currentmodule:: fooof.bands

.. autosummary::
   :toctree: generated/

   Bands

FOOOF Functions
---------------

.. currentmodule:: fooof.funcs

.. autosummary::
   :toctree: generated/

   average_fg
   combine_fooofs
   fit_fooof_group_3d

Analysis Functions
------------------

.. currentmodule:: fooof.analysis

.. autosummary::
    :toctree: generated/

    get_band_peak
    get_band_peak_fm
    get_band_peak_fg
    get_band_peak_group
    get_highest_peak

Sim Code
--------

Code & utilities for simulating power spectra.

Generating Power Spectra
~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.sim.gen

.. autosummary::
    :toctree: generated/

    gen_freqs
    gen_power_spectrum
    gen_group_power_spectra

Parameter Management
~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.sim.params

.. autosummary::
    :toctree: generated/

    Stepper
    param_iter
    param_sampler
    update_sim_ap_params

Transforming Power Spectra
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. currentmodule:: fooof.plts.spectra

.. autosummary::
    :toctree: generated/

    plot_spectrum
    plot_spectra
    plot_spectrum_shading
    plot_spectra_shading

Utility Functions
-----------------

.. currentmodule:: fooof.utils

.. autosummary::
    :toctree: generated/

    trim_spectrum
    get_info
    compare_info
