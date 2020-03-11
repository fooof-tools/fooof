Frequently Asked Questions
==========================

The following are a collection of frequently asked questions about FOOOF.

These answers focus on the ideas and concepts relating to parameterizing neural power spectra.

Code specific and hands-on aspects of using FOOOF are covered in the
`tutorials <https://fooof-tools.github.io/fooof/auto_tutorials/index.html>`_ and
`examples <https://fooof-tools.github.io/fooof/auto_examples/index.html>`_.

Table of Contents
-----------------
.. contents::
   :local:
   :backlinks: none

What is FOOOF?
~~~~~~~~~~~~~~

FOOOF is an open-source Python toolbox to parameterize neural power spectra.

In particular, FOOOF is a model driven approach that assumes that neurophysiological time
series are comprised of two separable components, reflecting periodic and aperiodic activity.
FOOOF does therefore rely on the assumption that these two components are indeed separable
components of the underlying data, though it is agnostic to their physiological origin and
putative functional roles.

FOOOF operates on frequency representation of neurophysiological times series (power spectra).
At it's core, FOOOF is a fitting procedure to measure these two components - the periodic and
aperiodic components - in power spectra. The full model fit consists of a parameterizing of these
aperiodic and periodic components, as well as a full (combined) model fit of the whole
power spectrum.

The full mathematical description of the model is described in the tutorials.

What do you mean by 'periodic' and 'aperiodic' activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By 'periodic' activity we mean features of the signal that are rhythmic, that are typically
referred to as oscillations. This does not require that periodic activity be continuous,
as oscillatory activity often exhibits as 'bursts' in the time series. In practice, putative
oscillations, reflecting periodic activity, are operationally defined and detectable by FOOOF
if they exhibit as band-limited power over and above the aperiodic component of the signal
in the power spectrum.

By 'aperiodic' activity we mean the arrhythmic component of the signal, that typically follow
a 1/f like function, whereby the power systematically decreases with increasing frequencies.

Why should I use FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~

Though we often focus on the periodic (rhythmic or oscillatory) components, neurophysiological
recordings of electromagnetic activity in the brain are composed of not only this periodic
activity, which is only sometimes present, but also includes aperiodic activity.

Both of these components of the signal, periodic and aperiodic activity, are known to be dynamic
and can vary both within and between subjects. These two components of the signal have very
different properties and interpretations, however many commonly applied analyses often
conflate changes between them, as they do not systematically separate these two aspects of
the data, potentially leading to misinterpretation of the results.

It is therefore of the utmost importance to explicitly measure both components of the signal
to be sure what is actually changing in the data. This is what FOOOF is designed to do.
By explicitly modeling and measuring both aperiodic and periodic components of the signal,
FOOOF allows for separating out and quantifying which features of the data are changing,
and in what ways.

Why is it important to measure aperiodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Historically, much more work has focused on periodic components of neural signals,
with a focus on measuring putative oscillatory activity and investigating their
properties and potential functional roles.

Though the aperiodic, or 1/f, component of the signal has long known to be present
in the data, more recent work has demonstrated that this aperiodic activity is dynamic,
and systematically varies both within [1_] and between [2_] subjects.

The dynamic properties of the aperiodic activity means that even if periodic activity
is still the focus of the analysis, quantification of such data must explicitly account
for aperiodic activity to appropriately measure what components of the data are actually
changing.

In addition, aperiodic components of neural signals may be important and interesting
in their own right as an interesting signal to investigate as potential biomarker.
For example, recent work has been investigating potential physiological interpretations
of aperiodic activity [3_] (see also below for more on this).

Why call it 'aperiodic'? Why not call it '1/f' or 'noise'?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What we now call the 'aperiodic' component of the signal has variously been called, by us and
others, either the '1/f' component activity of the signal (also referred to as 'scale free'),
or sometimes the 'background' activity, or '1/f noise' or 'background noise'.

We have moved away from these terms, as they are imprecise, and/or theoretically loaded. In
terms of calling it the '1/f', though the signal often approximates '1/f' over at least some
frequency ranges, it is not truly '1/f' across all frequencies.

From the physics perspective, '1/f' activity is sometimes referred to as 'noise',
as shorthand for 'statistical noise' or `coloured noise <https://en.wikipedia.org/wiki/Colors_of_noise>`_.
As well as not necessarily meeting technical definitions, referring to aperiodic neural activity
as noise in this way is also different however to how the terms 'signal' & 'noise' are typically
used in neuroscience, in terms of referring to a signal of interest and unwanted or artifactual
activity. We consider that the aperiodic could be the signal of interest for some investigations.
Therefore, we have moved away from this term so as not to imply it is either strictly statistical
noise, nor is it merely unwanted 'noise' in the recording.

For similar reasons, we have moved away from calling it 'background' activity, as this implies
a signal of interest in the foreground, and we consider that aperiodic activity is of
theoretical interest itself, and not merely the 'background' to periodic activity.

For these reasons, we prefer and use the term 'aperiodic' as a neutral description
of this component of the signal.

Why should I look for a peak to consider periodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Due to neural signals containing aperiodic neural activity, there will always be power
within any given frequency range. If the aperiodic activity changes, this measured power
could also change. All this can happen without any truly periodic activity being present
in the data. Even if there is periodic activity, quantifications of it can be confounded
by aperiodic activity.

To be able to argue that there is periodic activity, and measure whether it changes, one
should be able to observe a peak in the power spectrum, reflecting band specific power, over
and above the aperiodic activity in the data. Using peaks in the power spectrum as evidence for
periodic activity is an established idea (see, for example [4_]), which we here formalize into
a model quantification.

What if I don't identify a peak? Is there no periodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a peak is not detected, in the power spectrum, within a given frequency band, this is
consistent with there being no periodic activity at that frequency. Without a detected peak,
we argue that there is no evidence of periodic activity, at that frequency, over and
above the power as expected by the aperiodic activity. In this situation, one should be very
wary of interpreting activity at this frequency, as it is most likely to reflect aperiodic
activity.

However, we can, of course not prove a negative, and the absence of a detected peak does
therefore imply that there must be no periodic activity at that frequency band. There could
be very low power periodic activity, and/or periodic activity that is variable through time
(bursty) such as to not display a prominent peak across the analyzed time sample.

How should I interpret peaks? Are they equivalent to oscillations?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Peaks, defined as regions of power over and above the aperiodic background are considered
to be putative periodic activity. However, there is not necessarily a one-to-one mapping of
peaks, as detected by the FOOOF algorithm, and oscillations in the data.

One reason for this is that peaks are fit as gaussians, and multiple overlapping
gaussians can, in some cases, be fit to what one might otherwise consider to likely
comprise a single oscillatory component in the data. This is a consequence of fitting a
symmetric function (gaussians) to what can be an asymmetric peak power spectrum.

Because of this, it is often useful to focus on the dominant (highest power) peak within a
given frequency band from a FOOOF analysis, as this peak will offer the best estimate of
the putative oscillations center frequency and power. If analyzing bandwidth of extracted peaks,
than overlapping peaks should always be considered. FOOOF is not currently optimized for inferring
whether multiple peaks within a frequency band likely reflect distinct oscillations or not.

It can also be the case that peaks in the power spectrum may reflect harmonic power from an
asymmetric oscillation in the time domain [5_], and so a peak in a particular frequency range
does not necessarily imply that there is a true oscillation at that particular frequency in the data.
For example, an asymmetric wave at 10 Hz can exhibit power at a 20 Hz harmonic, but this does not
necessarily imply there are any 20 Hz rhythmic components in the signal. To investigate
potential harmonics arising from asymmetric periodic activity, one can use
`ByCycle <https://bycycle-tools.github.io/bycycle/>`_
a Python tool for analyzing neural oscillations and their properties cycle-by-cycle [5_].

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

We don't know. Exactly what the 'aperiodic' component of the signal is, in terms of where
it comes from, and what reflects is an open research question.

Descriptively, we know that aperiodic activity is always there, and is a prominent
component of the signal. This has been known for a long time, and there are many
hypotheses and ideas around about '1/f'-like and aperiodic properties of neural time series,
and what they might mean. Many of the ideas regarding the potential functional properties
of 1/f or 'scale-free' systems comes from work in physics and from the context of
dynamical systems [6_].

We, and others, also work on physiological models of where aperiodic activity might come
from. One such model, from the VoytekLab, explores the hypothesis that the
aperiodic properties of the local field potential arise from balanced activity in
excitatory and inhibitory activity (EI balance), and shows how changes in the aperiodic
properties of a signal can be predicted from changes in EI balance [3_].

What data can I use with FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FOOOF operates on power spectra derived from electrophysiological or magnetophysiological
time series, that measure local field potential (LFP) data - in the broad sense, covering
intracranial LFP data, electroencephalography (EEG), magnetoencephalography (MEG), and
electrocorticography (ECoG) / intracranial EEG (iEEG).

FOOOF should work across all of these modalities, and is broadly agnostic to the details
of the data. However, data from different modalities may require different settings.

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
  analyzing the distribution of FOOOF outputs per condition

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
used in a time-resolved manner, it can be applied in a sliding window fashion, which could
be used to estimate results analogous to a spectrogram. This functionality is not currently
directly included in FOOOF, but is a topic of ongoing work, and will hopefully be available soon.

Why is it called FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~

FOOOF stands for "fitting oscillations & one-over f".

This was a working title for the project that stuck as the name of the code and the tool.
We have somewhat moved away from referring to the components that FOOOF fits in this way,
now preferring to talk about periodic and aperiodic activity. FOOOF therefore is something
of a legacy name, for a tool for parameterizing neural power spectra.

How do I cite FOOOF?
~~~~~~~~~~~~~~~~~~~~

If you use FOOOF for analyses, or reference it's approach, please cite the bioRxiv
`preprint <https://doi.org/10.1101/299859>`_.

What colour is FOOOF?
~~~~~~~~~~~~~~~~~~~~~

FOOOF is orange.

References
----------
- [1_] Podvalny et al (2017). A Unifying Principle Underlying the Extracellular Field Potential
  Spectral Responses in the Human Cortex. DOI: 10.1152/jn.00943.2014

.. _1 : https://doi.org/10.1152/jn.00943.2014

- [2_] Voytek et al (2015). Age-Related Changes in 1/f Neural Electrophysiological Noise.
  DOI: 10.1523/JNEUROSCI.2332-14.2015

.. _2 : https://doi.org/10.1523/JNEUROSCI.2332-14.2015

- [3_] Gao, Peterson & Voytek (2017). Inferring synaptic excitation/inhibition balance from field potentials.
  DOI: 10.1016/j.neuroimage.2017.06.078

.. _3 : https://doi.org/10.1016/j.neuroimage.2017.06.078

- [4_] Buzsaki, Logothetis & Singer (2013). Scaling Brain Size, Keeping Timing: Evolutionary Preservation
  of Brain Rhythms. DOI: 10.1016/j.neuron.2013.10.002

.. _4 : https://doi.org/10.1016/j.neuron.2013.10.002

- [5_] Cole & Voytek (2019). Cycle-by-cycle analysis of neural oscillations. DOI: 10.1152/jn.00273.2019

.. _5: https://doi.org/10.1152/jn.00273.2019

- [6_] He (2014). Scale-free Brain Activity: Past, Present and Future. DOI: 10.1016/j.tics.2014.04.003

.. _6 : https://doi.org/10.1016/j.tics.2014.04.003
