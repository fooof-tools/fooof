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

FOOOF Object Functions
----------------------

.. currentmodule:: fooof.funcs

.. autosummary::
   :toctree: generated/

   combine_fooofs
   fit_fooof_group_3d

Analysis Functions
------------------

.. currentmodule:: fooof.analysis

.. autosummary::
    :toctree: generated/

    get_band_peak
    get_band_peak_group
    get_highest_amp_peak

Synth Code
----------

Generating Power Spectra
~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.synth.gen

.. autosummary::
    :toctree: generated/

    gen_freqs
    gen_power_spectrum
    gen_group_power_spectra

Parameter Management
~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.synth.params

.. autosummary::
    :toctree: generated/

    Stepper
    param_iter
    param_sampler

Transforming Power Spectra
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: fooof.synth.transform

.. autosummary::
    :toctree: generated/

    translate_spectrum
    translate_syn_spectrum
    rotate_spectrum
    rotate_syn_spectrum
    calc_rotation_offset

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
    get_settings
    get_data_info
    compare_settings
    compare_data_info
