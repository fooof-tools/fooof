Frequently Asked Questions
==========================

The following are a collection of frequently asked questions and answers about FOOOF.

These answers focus on the ideas and concepts relating to parameterizing neural power spectra.

For code related questions, check out the API listing, tutorials, and examples.

Table of Contents
-----------------
.. contents::
   :local:
   :backlinks: none

What is FOOOF?
~~~~~~~~~~~~~~

FOOOF is an open-source Python module for parameterizing neural power spectra.

The parameterization uses a model-driven approach that assumes that neurophysiological time
series are comprised of two separable components, reflecting periodic (or oscillatory) and
aperiodic activity.

This approach therefore does rely on the assumption that these two components are indeed separable
components of the underlying data, though it is agnostic to their physiological origin and
putative functional roles.

The parameterization approach operates on frequency representations of neurophysiological times
series (power spectra). At it's core, the module contains an algorithm to measure these two
components - the periodic and aperiodic components - in power spectra. The final model
of the neural power spectrum, consists of quantifications of each of the two components, as well as
a combined model fit of the whole power spectrum.

The full mathematical description of the model is described in the tutorials.

What is meant by 'aperiodic' activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By 'aperiodic' activity we mean non-periodic (or arrhythmic) activity, meaning activity that
has no characteristic frequency. For a general example, white noise, would be considered to
be an aperiodic signal.

In neural data, the aperiodic component of the signal, typically follows a 1/f-like distribution,
whereby power systematically decreases with increasing frequencies. Due to the aperiodic
component, in a neural power spectrum, there is power at all frequencies, though this does
not imply there is rhythmic power.

What is meant by 'periodic' activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By 'periodic' activity we mean features of the signal that are rhythmic, with activity
at a characteristic frequency. This kind of activity is typically referred to as
neural oscillations.

In practice, putative oscillations, reflecting periodic activity, are operationally defined
and detectable by the fitting algorithm if they exhibit as band-limited power over and above
the aperiodic component of the signal in the power spectrum. This 'peak' of power over the
aperiodic is taken as evidence of frequency specific power, distinct from the aperiodic component.

Note that this periodic activity need not be continuous, as oscillatory activity often
exhibits as 'bursts' in the time series, nor sinusoidal, as rhythmic neural activity is
often non-sinusoidal.

Why should I parameterize power spectra?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Though research often focuses on periodic (rhythmic or oscillatory) components, neurophysiological
recordings of electrophysiological neural activity contain not only periodic, but also aperiodic
activity. Since both components of the signal are dynamic, and overlapping, it is important to
consider and measure both components, even when focusing on one or the other.

Both the periodic and aperiodic components of the signal are known to be dynamic, varying both
within and between subjects. Since these components overlap, a measured change in the data
could relate to a change in one or the other (or both) of these components. The two components
have very different properties and interpretations, so it is important to clarify which aspect(s)
of the data are changing, and interpret the data accordingly.

Despite this, many commonly applied analyses often do not explicitly consider the two components
of the data, or try to separately measure them. Therefore, results from such analyses may conflate
the two components, leading to potential misinterpretation of the results.

It is therefore of the utmost importance to explicitly measure both components of the signal
to be sure what is actually changing in the data. This is the goal of parameterizing neural
power spectra. By explicitly modeling and measuring both aperiodic and periodic components
of the signal, parameterization allows for separating out and quantifying which features of
the data are present, and changing, and in what ways.

For more discussion and examples of the conceptual and methodological factors that
motivate parameterizing neural power spectra, see the
`motivations page <https://fooof-tools.github.io/fooof/auto_motivations/index.html>`_

Why is it important to measure aperiodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aperiodic activity has long known to be present in neural data, but has been less of a
research focus, as compared to periodic activity. Recent work has demonstrated
that aperiodic activity is dynamic, and systematically varies both within [1_] and between
[2_] subjects, and has suggested potential physiological interpretations of aperiodic activity
[3_] (see also below for more on this).

We consider measuring aperiodic activity to be important for two reasons:

- Aperiodic activity is always there, and it is dynamic. Even if periodic activity
  is the focus of the analysis, quantification of such data must explicitly account
  for aperiodic activity to appropriately measure which components of the data are actually
  changing.
- Aperiodic components of neural signals may be important and interesting in their own right
  as an interesting signal to investigate. This is motivated by findings that aperiodic activity
  is dynamic, correlates with other features of interest, and is of theoretical interest [1_, 2_, 3_].

Why call it 'aperiodic'? Why not call it '1/f' or 'noise', etc?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What we now call the 'aperiodic' component of the signal has variously been called, by us and
others: '1/f' activity, 'scale free' activity, 'background' activity, '1/f noise', or
'background noise', amongst other names.

We have moved away from all these terms, as we consider them to be somewhat imprecise
and and/or theoretically loaded. We use term 'aperiodic' as a neutral descriptive term.

The one-over-f terminology (1/f) stems from the observation that neural activity
often approximates a '1/f' distribution, whereby power decreases over increasing
frequencies. This is also sometimes referred to as 'scale-free', as this
pattern is independent of scale (occurs across all frequencies).
From the physics perspective, '1/f' activity is sometimes referred to as 'noise',
relating to `colored noise <https://en.wikipedia.org/wiki/Colors_of_noise>`_, which
is a description of 1/f patterns in power spectra.

However, neural data is often not truly '1/f' across all frequencies. For example, there can
be 'knees' in the aperiodic component, which are like 'bends' in the 1/f, which make it not
a true, single, 1/f process. One-over-f terminology also often implies theoretical notions,
that one might not always want to invoke. For these reasons, we have moved away from using
one-over-f related terms as standard terminology.

Within neuroscience contexts, aperiodic activity has also sometimes been referred to as
'noise' or as 'background activity'. This typically implies a 'signal vs noise' or 'foreground
vs background' framing, whereby the 'signal' or 'foreground' of interest is typically
periodic activity. In this context, calling it 'noise' or 'background' activity conceptualizes
aperiodic activity as unwanted or uninteresting signal components. However, we consider
that the aperiodic component may be a signal of interest, and not merely 'noise' or
'background' activity.

Overall, we have moved to using the term 'aperiodic' to relate to any activity that is,
descriptively, non-periodic. We prefer this term, as a neutral descriptor, to avoid
implying particular theoretical interpretations, and/or what aspects of the signal
or of interest for any particular investigation.

Why are spectral peak used as evidence of periodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Due to neural signals containing aperiodic activity, there will always be power within
any given frequency range. If this aperiodic activity changes, the measured power within
a predefined frequency range can also change. All this can occur without any truly periodic
activity being present in the data. Even if there is periodic activity, quantifications of it
can be confounded by aperiodic activity.

If there is truly band-specific periodic power in a signal, this should be evident as a
peak in the power spectrum [4_]. Frequency specific peaks are evidence of power over and
above the power of the aperiodic activity. Therefore, to detect periodic activity, and
to measure whether periodic activity, specifically, is changing, these 'peaks' in the
frequency spectrum can be used.

What if there is no peak? Is there no periodic activity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If, for a given frequency band, no peak is detected in the power spectrum, this is
consistent with there being no periodic activity at that frequency. Without a detected peak,
we argue that there is not evidence of periodic activity, at that frequency, over and
above the power as expected by the aperiodic activity. In this situation, one should be very
wary of interpreting activity at this frequency, as it is most likely reflects aperiodic
activity.

However, one cannot prove a negative, of course, and so the absence of a detected peak does not
imply that there is definitively no periodic activity at that particular frequency. There could
be very low power periodic activity, and/or periodic activity that is variable through time
(bursty) such as to not display a prominent peak across the analyzed time period.

How should peaks be interpreted? Are they equivalent to oscillations?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Peaks, defined as regions of power over and above the aperiodic component, are considered
to be putative periodic activity. However, there is not necessarily a one-to-one mapping
between power spectrum peaks, and oscillations in the data.

One reason for this is that sometimes overlapping peaks can be fit to what is may
be a single oscillatory component in the data. This can happen if the peak in the power
spectrum is asymmetric. Since peaks are fit with gaussians, the model sometimes fits
partially overlapping peaks to fit what may be a single asymmetric peak in the data.

Because of this, it is often useful to focus on the dominant (highest power) peak within a
given frequency band, as this peak will typically offer the best estimate of the putative
oscillation's center frequency and power.

If analyzing the bandwidth of extracted peaks, than overlapping peaks should always
be considered. The power spectrum model is not currently optimized for inferring whether
multiple peaks within a frequency band likely reflect distinct oscillations or not.

It can also be the case that peaks in the power spectrum may reflect harmonic power from an
asymmetric oscillation in the time domain [5_]. This means that a peak in a particular frequency range
does not necessarily imply that there is a true oscillation at that particular frequency in the data.
For example, an asymmetric, or 'sharp', wave at 10 Hz can exhibit power at a 20 Hz harmonic, but
this does not necessarily imply there are any 20 Hz rhythmic components in the signal.

To investigate potential harmonics arising from asymmetric periodic activity,
`ByCycle <https://bycycle-tools.github.io/bycycle/>`_
is a Python tool for analyzing neural oscillations and their waveform shape properties [5_].

Why is parameterizing neural power spectra different from other methods?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are many existing methods for analyzing periodic activity, and also other methods for
analyzing aperiodic activity. Most existing methods are designed to measure one or the other
signal component. Few methods attempt to explicitly separate and quantify both the periodic
and aperiodic components of the signal. This combined approach is a key factor that we
consider to be important for getting the measurements to work well. By jointly learning
both components, the method is more capable of quantifying which aspects of the data
are changing and in what ways.

More in depth analyses of the properties of the fitting algorithm, and systematic comparisons
with other methods (through simulations) are are also ongoing, to clarify when and how
this approach compares to different methods.

What data modalities can be used for parameterizing neural power spectra?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The power spectrum model can theoretically be applied to power spectra derived from any
electrophysiological or magnetophysiological signal of neural origin. In practice, this
covers 'field' data, meaning intracranial local field potential (LFP) data,
electroencephalography (EEG), magnetoencephalography (MEG), and
electrocorticography (ECoG) / intracranial EEG (iEEG).

The power spectrum model should be applicable to all of these modalities, as long as the data
broadly match the data model, which is that the data can be described as a combination of
aperiodic and periodic activity. As long as this conception of the data is appropriate,
the model can be fit. The fitting algorithm is otherwise broadly agnostic to details of the data.
Note that data from different modalities, or across different frequency ranges, may require
different algorithm settings.

More information for checking for if the model fit seems to be appropriate, and for picking
settings and tuning them to different datasets are all available in the Tutorials.

Are there settings for the fitting algorithm?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, there are some settings for the algorithm. The algorithm is initialized with default
values that are often good enough to get started with fitting, but these settings will often
need some tuning to optimize fitting on individual datasets.

A full description of the settings - what they are and how to choose them -
is covered in the tutorials.

How should algorithm settings be chosen?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For any given dataset, there is often some tuning of the algorithm settings needed to
get models to fit well. For any given dataset, settings should therefore be checked, and
tuned if necessary, though, overall, model fits tend not to be overly sensitive to small
changes in the settings.

One strategy for choosing settings, is to select a subset of power spectra from the
dataset to use as something analogous to a 'training set'. This group of spectra can be
used to fit power spectrum models, check model fit properties, visually inspect fits, and
choose the best settings for the data. Once settings have been chosen for the subset,
they can applied to the dataset to be analyzed. Note that in order to be able to systematically
compare model fits between conditions / tasks / subjects, etc, we recommend using the same
algorithm settings across the whole dataset.

Details of what the algorithm settings are, and how to set them are available in the code Tutorials.

What frequency range should the model be fit on?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The frequency range used to fit a power spectrum model depends on the data and the questions
of interest. As a general guideline, one typically wants to use relatively broad ranges.
This best allows for fitting the aperiodic activity, which in turn allows for better
detecting peaks.

For example, for an M/EEG analysis investigating low frequency oscillatory bands
(theta, alpha, beta), a fitting range around [3, 35] may be a good starting point.
By comparison, an analysis in ECoG that wants to include high frequency activity might
use a range of [1, 150], or perhaps [50, 150] if the goal is to focus specifically on
high frequency activity.

Picking a frequency range should be considered in the context of choosing the
aperiodic mode, as whether or not a 'knee' should be fit depends in part on the frequency
range that is being examined. For more information on choosing the aperiodic mode, see the Tutorials.

If I am interested in a particular oscillation band, should I fit a small range?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally, no - it is better to always try and fit a broad frequency range, rather than to
fit a small range, even if one is interested in a specific oscillation band.

This is because if a small frequency range is used, it becomes much more difficult to
estimate the aperiodic component of the data, because so much of the activity in that range is
dominated by the peak. Without a good estimate of the aperiodic component, it can also be more
difficult to estimate and separate the periodic component from the aperiodic activity,
leading to potentially bad fits.

Therefore, if one is interested in, for example, alpha oscillations (approximately 7-14 Hz),
then we still recommend fitting a broad range (for example, 3-40 Hz), and then extracting the
alpha oscillations post-hoc. There are utilities in `analysis` module of the package for
extracting peaks from particular bands, and examples of this on the examples page.

What does the 'aperiodic' component of the signal reflect?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basically, we don't know. Exactly what the 'aperiodic' component of the signal is,
in terms of where it comes from, and what reflects is an open research question.

Descriptively, we know that aperiodic activity is always there, and is a prominent
component of neural data. This has been known for a long time, and there are many
hypotheses and ideas around about aperiodic properties of neural time series,
and what they might mean. Many of the ideas regarding the potential functional properties
of 1/f or 'scale-free' systems comes from work in physics and from the context of
dynamical systems [6_].

There are also physiological models of where aperiodic activity might come from.
One such model, explores the hypothesis that the aperiodic properties of local field
potential arise from balanced activity of excitatory (E) and inhibitory (I) synaptic
currents. In this model, changes in aperiodic properties of the data relate to changes
in EI balance [3_].

Does it matter how power spectra are calculated?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the most part, it does not matter exactly how power spectra to be parameterized
are calculated. The algorithm is agnostic to precise details of calculating power
spectra, and so different estimation methods should all be fine.

Regardless of how power spectra are computed, certain properties of the power spectra do
influence how the parameterization goes. For example, the better the frequency resolution,
the more precisely the algorithm will be able to estimate center frequencies and bandwidths
of detected peaks. However, as a trade off, using longer time segments to end up with 'smoother'
spectra can also help with getting the algorithm to fit better.

Can this be applied to task or trial based analyses?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, power spectra can be fit in task based analyses.

However, one thing to keep in mind is the resolution of the data. The shorter the
time segments of data used, and/or the fewer data segments averaged over, can lead to
'messy' power spectra, which may not be fit very well by the model.

With these considerations in mind, there are broadly two approaches for task related analyses:

- Calculate FFT's or power spectra per trial, and average across all trials in a condition,
  fitting one power spectrum model per condition

  - This doesn't allow for measurements per trial, but averaging across trials allows
    for smoother spectra, and better model fits, per condition. This approach may be
    for short trials, as the trial averaging allows want to use FOOOF to characterize
    short time segments in a task design.

- Calculate power spectra and fit power spectrum models per trial,
  analyzing the distribution of model parameters outputs per condition

  - This approach can be used with longer trials, when there are relatively long time
    segments to fit. Model fits of individual trials are likely to be somewhat messy, but
    as long as there is not a systematic bias in the fits, then the distributions of fit values
    can be interpreted and compared.
  - Exactly how much long segments need to to be analyzed in this way is somewhat
    dependent on the cleanliness of the data. As a rule of thumb, we currently recommend
    using segments of at least about 500 ms for this approach.

Ultimately, in theory these two approaches should converge to be equivalent, however,
in practice there may be some differences. Depending on the data and analysis goals,
one or the other might be more appropriate.

Is there a time resolved version?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since it operates on frequency representations (power spectra) the power spectrum model is not,
by construction, a time resolved method.

However, similar to other frequency estimation approaches that are used in a time-resolved manner,
it can, in theory, be applied in a sliding window fashion. This approach could be used to estimate
spectral features across time, somewhat analogous to a spectrogram.

This functionality is not currently available or described in the current module, but is a focus
off current work. We hope to add information, guidelines, and tooling to do this once this soon.

Why is it called FOOOF?
~~~~~~~~~~~~~~~~~~~~~~~

FOOOF stands for "fitting oscillations & one-over f".

This was a working title for the project that stuck as the name of the code and the tool.
We have moved away from referring to the components that FOOOF fits in this way, preferring
'periodic' and 'aperiodic' activity, but the name 'FOOOF' stuck around as the name of the tool
itself.

How do I cite this method?
~~~~~~~~~~~~~~~~~~~~~~~~~~

See the `reference <https://fooof-tools.github.io/fooof/reference.html>`_ page
for notes on how to report on using the algorithm and how to cite it.

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
