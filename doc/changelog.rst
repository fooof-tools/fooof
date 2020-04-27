Code Changelog
==============

This page contains the changelog for the FOOOF codebase and any notes on updating between versions.

This page primarly notes changes for major version updates. For notes on the specific updates
for minor releases, see the `release page <https://github.com/fooof-tools/fooof/releases>`_.

1.0.0
-----

Warning: the 1.X.X release series is an API breaking release from the from 0.X.X series.

That is it say, that some names and module organizations have changed, and you should
only update if and when you are ready to update your code to reflect the new changes.

Note that the main changes are in code organization, some names, and the addition of
many new features. The fitting algorithm itself has not changed, and model results fit
with the new version should be roughly equivalent to those with older versions. However,
there are bug fixes and tweaks such that new model fits are not guaranteed to be the
identical to prior fits.

Naming Updates
~~~~~~~~~~~~~~

The following is a list of the key naming updates, of public facing code.

- the `synth` module is now called them `sim` module
- references to `background` are now called `aperiodic`

  - setting `background_mode` -> `aperiodic_mode`
  - attribute `background_params_` -> `aperiodic_params_`
  - short name `bg` is now replaced with `ap`
- `slope` is now called `exponent`
- `amplitude`, in reference to peaks, is now called `height`

  - setting `min_peak_amplitude` -> `min_peak_height`
  - References to `AMP` are now labelled and accessed as `PW` (for 'power')

Previously Saved Data
~~~~~~~~~~~~~~~~~~~~~

Note that if you have data saved out from the 0.X.X release series of the module, then the
code update to the 1.X.X series won't be able to properly load this data out of the box.

This is due to the naming changes, and in particular the change from 'background' to
'aperiodic'. Note that saved FOOOF files are plain-text JSON files, and so if you find & replace
the word 'background' to 'aperiodic', this should update the files so that they can be loaded by
the 1.X.X version. Note that if you also saved out the algorithm settings, you may need to update
the name of `min_peak_amplitude` to `min_peak_height` as well.

Code Organization
~~~~~~~~~~~~~~~~~

The internal organization of the module has been changed - though the main functions and
objects can still be imported the same as in the 0.X.X series. The internal organization
changes typically reflect turning internal files into sub-modules.

Code Updates
~~~~~~~~~~~~

This version adds a large number of code updates & additions, including:
- A big extension of the plotting sub-module
- Adding new functions to manipulate, manage, organize and manage FOOOF objects
- Add new analysis functions, including more utilities for checking model errors
- Add a new 'Bands' object for managing frequency band definitions
- Extra methods on FOOOF & FOOOFGroup objects for managing data & results
- Miscellaneous bug fixes & other additions

To see all the new features in FOOOF, check out the API page on documentation site.

The full history of changes is avaible in the Github commit and pull request history.
The bulk of the updates for 1.X.X went through in the following pull requests:
- #152: broad updates, including lots of issue fixes, and code & documentation extensions
- #139: add 'Bands' object and more functions for managing FOOOF objects
- #130: updates data objects and internal data management
- #121 & #129: code reorganizations & cleanups
- #122: Updating terminology and names

Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

The 1.X.X series comes with a greatly updated documentation site, in which as well as
updating the tutorials and existing documentation, there are a large number of extra
examples, and a new 'motivations' section, exploring why 'parameterizing neural power spectra'
is a useful idea & method.

0.1.X
-----

The 0.1.X series of releases for FOOOF was the initial release series of FOOOF, with the original naming scheme. This series is now deprecated.

These releases can still be accessed, and are described, on the
`release page <https://github.com/fooof-tools/fooof/releases>`_
