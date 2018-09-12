Frequently asked questions
==========================

Why should I use FOOOF?
-----------------------

Because it's super-duper fun.


How do I pick settings?
-----------------------

Quick version: start at best guess, check plots and go from there [Note: recommend 'train / test' split]


I'm interested in a particular oscillation band, should I fit a small range?
----------------------------------------------------------------------------

Generally, no, always try and fit a broad range


So what is slope anyways?
-------------------------

Point to Gao et al, 2017.


What data does this work on?
----------------------------

Basically, any power spectra from neuro-electrophysiological field data

How should I make the power spectra? Does it matter?
----------------------------------------------------

It doesn't really matter.


Why is this different from prior things / what makes it work?
-------------------------------------------------------------

Broadly: by jointly learning aperiodic & periodic, and in particular, gains in slope fitting (otherwise: once one thing goes awry, everything else fails apart with it.)

Does this work on epoched data? Is there a time resolved version?
-----------------------------------------------------------------

Yes.