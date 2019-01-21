.. _api_documentation:

=================
API Documentation
=================

.. currentmodule:: fooof

FOOOF Object
============

.. autosummary::
   :toctree: generated/

   FOOOF

FOOOFGroup Object
=================

.. autosummary::
   :toctree: generated/

   FOOOFGroup
   fit_fooof_group_3d

Analysis Functions
==================

.. autosummary::
    :toctree: generated/

    analysis.get_band_peak
    analysis.get_band_peak_group

Synthesis Functions
===================

.. autosummary::
    :toctree: generated/

    synth.Stepper
    synth.param_iter
    synth.param_sampler
    synth.gen_power_spectrum
    synth.gen_group_power_spectra
    synth.rotate_spectrum

Plotting Functions
==================

.. autosummary::
    :toctree: generated/

    plts.spectra.plot_spectrum
    plts.spectra.plot_spectra
    plts.spectra.plot_spectrum_shading
    plts.spectra.plot_spectra_shading
    plts.fm.plot_fm
    plts.fm.plot_peak_iter
    plts.fg.plot_fg

Utility Functions
=================

.. autosummary::
    :toctree: generated/

    utils.trim_spectrum
    utils.get_settings
    utils.get_data_info
    utils.compare_settings
    utils.compare_data_info
    utils.combine_fooofs

Data Objects
============

.. autosummary::
    :toctree: generated/

    fit.FOOOFResult
