Code Changelog
==============

This page contains the changelog for the `specparam` / `fooof` module,
including release notes and guidance on updating between versions.

This page primarily notes changes for major version updates.
For notes on the specific updates for minor releases, see the
`release page <https://github.com/fooof-tools/fooof/releases>`_.

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
in the beta series (0.X.X). It is a stable release version of the module.

As compared to the prior series (0.X.X), some names and module organizations have changed.
This means existing code that uses FOOOF may no longer work as currently written with the
new version, and may need updating. You should update to the new version when you are ready to
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
- Adding new functions to manipulate, manage, organize and manage FOOOF objects
- Add new analysis functions, including more utilities for checking model errors
- Add a new 'Bands' object for managing frequency band definitions
- Extra methods on FOOOF & FOOOFGroup objects for managing data & results
- Miscellaneous bug fixes & other additions

The full history of changes is available in the Github commit and pull request history.

The bulk of the updates for 1.X.X went through in the following pull requests:

- #152: broad updates, including lots of issue fixes, and code & documentation extensions
- #139: add 'Bands' object and more functions for managing FOOOF objects
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
'aperiodic'. Note that saved FOOOF files are plain-text JSON files, and so if you find & replace
the word 'background' to 'aperiodic', this should update the files so that they can be loaded by
the 1.X.X version. Note that if you also saved out the algorithm settings, you may need to update
the name of `min_peak_amplitude` to `min_peak_height` as well.

0.1.X
-----

The 0.1.X series was the initial release series of beta versions of the FOOOF module.

The old series of releases has a different naming scheme and module organization to the
current 1.X.X series, and is now deprecated, with no plans to update or maintain this version.

These releases are described, and can still be accessed, on the
`release page <https://github.com/fooof-tools/fooof/releases>`_
