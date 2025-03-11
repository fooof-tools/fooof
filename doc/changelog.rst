Code Changelog
==============

This page contains the changelog for the `specparam` / `fooof` module,
including release notes and guidance on updating between versions.

This page primarily notes changes for major version updates.
For notes on the specific updates for minor releases, see the
`release page <https://github.com/fooof-tools/fooof/releases>`_.

2.0.0 (in development)
----------------------

WARNING: the specparam 2.0 release is not yet a a stable release, and may still change!

Note that the new `specparam 2.0` version includes a significant refactoring or the internals of the module, and broad changes to the naming of entities (including classes, functions, methods, etc) across the module. As such, this update is a major, breaking change to the module (see below for updates). See below for notes on the major updates, and relationships to previous versions of the module.

Key Updates
~~~~~~~~~~~

The `specparam` 2.0 version contains the following notable feature updates:

- an extension of the module to support time-resolved and event-related analyses

  - these analyses are now supported by the ``SpectralTimeModel`` and ``SpectralTimeEventModel`` objects

- an update to procedures for functions that are fit to power spectra

  - these updates allow for flexibly using and defining different fit functions [WIP]

- an update to procedures for defining and applying spectral fitting algorithms

  - these updates allow for choosing, tuning, and changing the fitting algorithm that is applied [WIP]

- extensions and updates to the module

  - this includes updates to parameter management, goodness-of-fit evaluations, visualizations, and more

The above notes the major changes and updates to the module - for further details on the changes, see the
`release page <https://github.com/fooof-tools/fooof/releases>`_.

Relationship to fooof
~~~~~~~~~~~~~~~~~~~~~

As compared to the fooof releases, the specparam module is an extension of the spectral parameterization approach, including the same functionality as the original module, with significant extensions. This means that, for example, if choosing the same fit functions and algorithms in specparam 2.0 as are used in fooof 1.X, the results should be functionally identical.

Notably, there are no changes to the default settings and models in specparam 2.0, such that fitting a spectral model with the default settings in specparam should provide the same as doing the equivalent in fooof 1.X.

Naming Updates
~~~~~~~~~~~~~~

The following functions, objects, and attributes have changed name in the new version:

Model Objects:

- FOOOF -> SpectralModel
- FOOOFGroup -> SpectralGroupModel

Model Object methods & attributes:

- FOOOF.fooofed_spectrum\_ -> SpectralModel.modeled_spectrum\_
- FOOOFGroup.get_fooof -> SpectralGroupModel.get_model

Data objects:

- FOOOFResults -> FitResults
- FOOOFSettings -> ModelSettings
- FOOOFMetaData -> SpectrumMetaData

Functions:

- combine_fooofs -> combine_model_objs
- compare_info -> compare_model_objs
- average_fg -> average_group
- fit_fooof_3d -> fit_models_3d

- get_band_peak_fm -> get_band_peak
- get_band_peak_fg -> get_band_peak_group
- get_band_peak -> get_band_peak_arr
- get_band_peak_group -> get_band_peak_group_arr

- compute_pointwise_error_fm -> compute_pointwise_error
- compute_pointwise_error_fg -> compute_pointwise_error_group
- compute_pointwise_error -> compute_pointwise_error_arr

- save_fm -> save_model
- save_fg -> save_group

- fetch_fooof_data -> fetch_example_data
- load_fooof_data -> load_example_data

- gen_power_spectrum -> sim_power_spectrum
- gen_group_power_spectra -> sim_group_power_spectra

Function inputs:

- fooof_obj -> model_obj

1.1.0
-----

The 1.1.X release is a minor (non-breaking) update to the 1.X.X release series.
More detailed information on what is updated in 1.1.0 is on the release page.

Note that 1.1.0 is the last planned release in the 1.X.X, and under the `fooof` name.
All future development will be under the new `specparam` module name, starting with
the upcoming `specparam 2.0.0` release.

1.0.0
-----

Warning: the 1.X.X release series is an API breaking release from the prior versions,
in the beta release series (0.X.X). It is a stable release version of the module.

As compared to the prior series (0.X.X), some names and module organizations have changed.
This means existing code may no longer work as currently written with the new version,
and may need updating. You should update to the new version when you are ready to
update your code to reflect the new changes.

Note that the main changes are in code organization, some names, and the addition of
many new features. The fitting algorithm itself has not changed, and model results fit
with the new version should be roughly equivalent to those with older versions. However,
there are bug fixes and tweaks such that new model fits are not guaranteed to be the
identical to prior fits.

Code Organization
~~~~~~~~~~~~~~~~~

The internal organization of the module has changed with the 1.X.X series.

These internal organization changes mostly reflect turning internal files into
sub-modules. Overall, this means that although the main functions and objects can
still be imported the same as in the 0.X.X series, some items have changed name or moved.

To see the new names and organization of the module, check the
`API page <https://fooof-tools.github.io/fooof/api.html>`_.

Naming Updates
~~~~~~~~~~~~~~

There are a series of name changes with the new 1.X.X series.

These name changes were done to update the module to reflect the current vocabulary
and conceptual ideas relating to work on parameterizing neural power spectra.

The main name changes are:

- the `synth` module is now called them `sim` module
- references to `background` are now called `aperiodic`

  - setting `background_mode` -> `aperiodic_mode`
  - attribute `background_params_` -> `aperiodic_params_`
  - short name `bg` is now replaced with `ap`
- `slope` is now called `exponent`
- `amplitude`, in reference to peaks, is now called `height`

  - setting `min_peak_amplitude` -> `min_peak_height`
  - References to `AMP` are now labeled and accessed as `PW` (for 'power')

Code Updates
~~~~~~~~~~~~

The 1.X.X series adds a large number of code updates & additions, including:

- A big extension of the plotting sub-module
- Adding new functions to manipulate, manage, organize and manage model objects
- Add new analysis functions, including more utilities for checking model errors
- Add a new 'Bands' object for managing frequency band definitions
- Extra methods on model objects for managing data & results
- Miscellaneous bug fixes & other additions

The full history of changes is available in the Github commit and pull request history.

The bulk of the updates for 1.X.X went through in the following pull requests:

- #152: broad updates, including lots of issue fixes, and code & documentation extensions
- #139: add 'Bands' object and more functions for managing model objects
- #130: updates data objects and internal data management
- #121 & #129: code reorganizations & cleanups
- #122: Updating terminology and names

Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

The 1.X.X series comes with an updated documentation site.

As well as updating the tutorials, API list, and other existing documentation, there are
also new materials, including:

- new examples, including new pages that cover new functionality
- a new 'motivations' section, exploring why 'parameterizing neural power spectra' is a useful idea & method
- new or updated sections on frequently asked questions, a module glossary, and how to reference the module

A Note on Previously Saved Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that if you have data saved out from the 0.X.X release series of the module, then the
code update to the 1.X.X series won't be able to properly load this data out of the box.

This is due to the naming changes, and in particular the change from 'background' to
'aperiodic'. Note that saved files are plain-text JSON files, and so if you find & replace
the word 'background' to 'aperiodic', this should update the files so that they can be loaded by
the 1.X.X version. Note that if you also saved out the algorithm settings, you may need to update
the name of `min_peak_amplitude` to `min_peak_height` as well.

0.1.X
-----

The 0.1.X series was the initial release series of beta versions of the module.

The old series of releases has a different naming scheme and module organization to the
current 1.X.X series, and is now deprecated, with no plans to update or maintain this version.

These releases are described, and can still be accessed, on the
`release page <https://github.com/fooof-tools/fooof/releases>`_
