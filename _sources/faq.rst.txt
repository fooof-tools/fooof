Frequently Asked Questions
==========================

The following are a collection of frequently asked questions
the ideas and design of FOOOF.

These answers do not cover code specific things, as the hands-on
aspects of using FOOOF are covered in the Tutorials & Examples.

Table of Contents
-----------------
.. contents::
   :local:
   :backlinks: none

What is FOOOF?
~~~~~~~~~~~~~~

FOOOF is an open-source Python toolbox to parameterize neural power spectra.

In particular, FOOOF is a model driven approach that assumes that neurophysiological times
series are comprised of two separable components, reflecting periodic and aperiodic activity.
FOOOF does therefore rely on the assumption that these two components are indeed separable
components of the underyling data, though it is agnostic to their physiological origin and
putative functional roles.

FOOOF operates on frequency representation of neurophysiological times series (power spectra).
At it's core, FOOOF is a fitting procedure to measure these two components, periodic and
aperiodic, in the power spectrum. The full model fit consists of a parameterizing of these
aperiodic and periodic components, as well as a full (combined) model fit of the whole
power spectrum.

The full mathematical description of the model is described in the tutorials.

Why is it called FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~

FOOOF stands for "fitting oscillations and one-over f".

This was a working title for the project that stuck as the name of the tool. The way we think
of it now is in terms of being a tool for parameterizing neural power spectra and,
in particular, as tool for measuring both periodic and aperiodic activity in neural time series.

Why should I use FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~

Though we often focus on the rhythmic (periodic) components, neurophysiological recordings
of electromagnetic activity in the brain are fundamentally composed of aperiodic activity
upon which there is (sometimes) also rhythmic components.

Both of these components of the signal, periodic and aperiodic activity, are known to be dynamic
and can vary both within and between subjects. These two components of the signal have very
different properties and interpretations, however many commonly applied analysis can often
conflate changes between them, as they do not systematically separate these two aspects of
the data, potentially leading to misinterpration of the results.

It is therefore of the utmost importance to explicitly measure both components of the signal
to be sure what is actually changing in the data. This is what FOOOF is designed to do,
by explicitly modelling and measuring both aperiodic and periodic components of the signal.

Why is it important to measure aperiodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Historically, much more work has focused on periodic components of neural signals,
with a focus on measuring oscillatory activity and investigating their properties
and potential functional roles.

Though the aperiodic, or 1/f, component of the signal has long known to be present
in the data, more recent work has demonstrated that this aperiodic activity is dynamic,
and systematically varies both
`within <http://www.weizmann.ac.il/neurobiology/labs/malach/sites/neurobiology.labs.malach/files/Podvalny%20et%20al_2015_JNeurophysiol.pdf>`_ and
`between <http://voyteklab.com/wp-content/uploads/Voytek-JNeurosci2015.pdf>`_ subjects.

The dynamics properties of the aperiodic activity means that even if periodic activity
is still the focus of the analysis, quantification of such data must explicitly account
for aperiodic activity to appropriately measure what components of the data are actually
changing. In addition, this suggests that aperiodic components of neural signals may be
important in their own right as an interesting signal to investigate as potential biomarker,
with ongoing work also investigating it's potential
`physiological interpretations <http://voyteklab.com/wp-content/uploads/Gao-NeuroImage2017.pdf>`_
(see also below for more on this).

What do you mean by 'periodic' and 'aperiodic' activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By 'periodic' activity we mean features of the signal that are rhythmic, that are typically
referred to as oscillations. This does not require that periodic activity be continuous,
as oscillatory activity often exhibits as 'bursts' in the time series. In practice, putative
oscillations, reflecting periodic activity, are operationally defined and detectable by FOOOF
if they exhibit as band-limited power over and above the aperiodic component of the signal
in the power spectrum.

By 'aperiodic' activity we mean the arhythmic component of the signal, that typically follow
a 1/f like function, whereby the power systematically decreases with increasing frequencies.

Why call it 'aperiodic'? Why not call it '1/f' or 'noise'?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What we now call the 'aperiodic' component of the signal has variously been called, by us and
others, either the '1/f' component activity of the signal (also referred to as 'scale free'),
or sometimes the 'background' activity, or '1/f noise' or 'background noise'.

We have moved away from these terms, as they are imprecise, and/or theoretically loaded. In
terms of calling it the '1/f', though the signal often approximates '1/f' over at least some
frequency ranges, it is not truly '1/f' across all frequencies.

Also, from the physics perspective, '1/f' like activity is sometimes referred to as 'noise',
as shorthand for 'statistical noise'. This is different however to how the terms 'signal' &
'noise' are typically used in neuroscience, and so we have moved away from this term so as
not to imply it is merely 'noise'. For similar reasons, we have moved away from calling it
'background' activity, as the aperiodic properties are of theoretical interest themself, and
not merely the 'background' to periodic activity.

For these reasons, we prefer and use the term 'aperiodic' as a neutral description
of this component of the signal.

Why is this different from other methods / what makes it work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many existing approaches do not attempt to separate the periodic and aperiodic components of
the signal. Of methods that do attempt to measure periodic and/or aperiodic signal properties,
one difference is that FOOOF does not prioritize one or the other component, but attempts to
jointly learn both components.

As a quick version, the joint learning procedure and some developments in fitting the aperiodic
component are why we think FOOOF seems to do better at measuring these signal properties.
More in depth analysis of the properties of FOOOF, and systematic comparisons with other methods
(through simulations) are upcoming.

Are there settings for the FOOOF algorithm?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are some settings for the algorithm that need to be set before it can be run, though the
default values are often good enough to get started on most datasets.

A full description of the settings - what they are and how to choose them -
is covered in the tutorials.

How do I pick settings?
~~~~~~~~~~~~~~~~~~~~~~~

There is often at least some level of picking the parameter settings that is needed to get
FOOOF to fit well. To do so, we recommend selecting a subset of power spectra from your
dataset, fitting FOOOF models, and tuning the settings on this dataset, like a training set.
Once you have chosen the parameters for the dataset, you can apply these settings to the
data to be analyzed.

In order to be able to systematically compare FOOOF model outputs between conditions / tasks
/ subjects, etc, we recommend using the same FOOOF settings across any particular dataset.

FOOOF tends not to be overly sensitive to small changes in parameter settings. You can also
perform a sensitivity analysis - repeating the analysis with different settings - to examine
if the outputs are strongly dependent on the settings you choose.

I'm interested in a particular oscillation band, should I fit a small range?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally, no, it is better to always try and fit a broad range, rather than to fit a small
frequency range, even if one is interested in a specific oscillation band in particular.

This is because the if a small frequency range is used, it becomes much more difficult to
estimate the aperiodic component of the data, and without a good estimate of the aperiodic
component, it can also be more difficult to effectively estimate the periodic components.

Therefore, if one is interested in, for example, alpha oscillations (approximately 7-14 Hz),
the we still recommend fitting a broad range (for example, 3-40 Hz), and then extracting the
alpha oscillations post-hoc. There are utilities in fooof.analysis to extract oscillations
from particular bands, and examples of this on the examples page.

What does the 'aperiodic' component of the signal mean / reflect?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exactly what the 'aperiodic' component of the signal is / reflects is an open research question.
We just know it is there, and is a prominent component of the signal. There are a series of
hypotheses / ideas from us and others about '1/f' like and aperiodic properties of neural
time series, including functional models from the context of dynamical systems, as well as
physiological models of where these signals might come from.

One such physiological model, from the VoytekLab, explores the hypothesis that the
aperiodic properties of the local field potential arise from balanced activity in
excitatory and inhibitory activity (EI balance), and shows how changes in the aperiodic
properties of a signal can be predicted from changes in EI balance, which you can
read about `here <https://doi.org/10.1016/j.neuroimage.2017.06.078>`_

What data can I use with FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FOOOF operates on power spectra derived from electrophysiological or magnetophysiological
time series, that measure local field potential (LFP) data - in the broad sense, covering
intracranial LFP data, electroencephalography (EEG), magnetoencephalography (MEG), and
electrocorticograpgy (ECoG) / intracranial EEG (iEEG).

Within these modalities, FOOOF is broadly agnostic to the details of the data, and
can be applied pretty generally, though data from different modalities may require
somewhat different settings in the FOOOF algorithm.

Does it matter how I calculate the power spectra?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the most part, no, it does not matter exactly how you calculate power spectra that
you will fit with FOOOF. For example, using different methods to estimate the power
spectrum, such as Welch's or wavelet approaches, should all be fine.

Regardless of how you calculate them, the properties of the power spectra do matter somewhat
to FOOOF - for example, the better the frequency resolution the more resolution you will have
for estimating center frequencies and bandwidths of detected peaks, and the 'smoother'
the spectra, the better FOOOF will be able to fit.

Does this work on epoched data? Can I fit single trials?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, FOOOF can be used in task based analyses.

There are broadly two approaches you can take:

- Calculate FFT's or power spectra per trial, and average across all trials in a condition,
  to fit one FOOOF model per condition

  - This approach is better if you want to use FOOOF to characterize
    short time segments in a task design

- Calculate power spectra per trial, and fit FOOOF models per trial,
  analyzing the ditribution of FOOOF outputs per condition

  - This approach can be used when you have relatively long time segments to fit.
    We currently recommend at least about 500 ms for using this approach, though
    it is somewhat dependent on the cleanliness of the data, and what aspects of
    the FOOOF outputs you want to analyze.

Ultimately these two approaches should converge to be the same, though depending on
the data and analysis goals, one or the other might be more appropriate.

Is there a time resolved version?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since it operates on frequency representations (power spectra) FOOOF is not, by construction,
a time resolved method. However, similar to other frequency estimation approaches that are
used in a time-resovled manner, it can be applied in a sliding window fashion, which could
be used to estimate results analogous to a spectrogram. This functionality is not currently
directly included in FOOOF, but hopefully will be soon.

How do I cite FOOOF?
~~~~~~~~~~~~~~~~~~~~

If you use FOOOF for analyses, or reference it's approach, please cite the
bioarxiv `preprint <https://doi.org/10.1101/299859>`_

What colour is FOOOF?
~~~~~~~~~~~~~~~~~~~~~

FOOOF is orange.
