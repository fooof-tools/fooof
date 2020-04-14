Glossary
========

A glossary of terms used in the module, with a description of how they are used, as well as common abbreviations.

.. glossary::

    FOOOF
        FOOOF stands for 'fitting oscillations & one-over f'.
        We use `FOOOF` to refer to either the current module, or to `FOOOF` objects.

    Field Data
        'Field data' is used as a catch-all for the relevant types of data that the power spectrum model can be applied to. This includes recordings of electrophysiological or magnetophysiological 'fields', meaning recording modalities such as electroencephalography (EEG), magnetoencephalography (MEG), electrocorticography (ECoG), and local field potential (LFP) data.

    Power Spectrum
        A power spectrum (short for power spectral density) describes the distribution of power across frequencies.

    Power Spectrum Model
        A power spectrum is a model that describes neural power spectra.
        This module implements a particular power spectrum model, whereby we conceptualize and describe mathematically a model that considers power spectra as a combination of periodic and aperiodic components, each of which can be described by a set of model parameters.

    FOOOF Objects
        This module is object-oriented, whereby the algorithm to parameterize neural power spectra is implemented in Python objects. We refer to those objects as 'FOOOF objects'.

    Component
        By 'component' we mean a part, or aspect, of the data.
        Different components of the data are considered to be separate aspects of, or entities in, the data, (though they need not be be completely independent).

    Parameters
        We use the term 'parameters' to describe the parameters of the model, meaning the values in the model that are fit to the data. These model parameters are the results of the model fitting.

    Settings
        We use 'settings' to refer to things that control the algorithm, or any the settings for the algorithm that can be used to adjust the fitting procedure.

    Periodic
        Periodic (or 'rhythmic') component(s) of the data, that reflect putative oscillations.

    Peaks
        Parts of the power spectrum that are identified to have power over and above the aperiodic component, and are thus modeled as 'peaks', reflecting putative oscillations. The set of identified peaks are the periodic component(s) of the data. The peaks are described by the peak parameters: center frequency (CF), power (PW), and bandwidth (bw).

    Aperiodic
        Aperiodic (or 'arrhythmic') components of the data.
        In neural power spectra, by aperiodic activity, we typically mean the 1/f-like activity.

    One-Over F (1/f)
        'One over f' or '1/f' activity describes activity whereby the power spectrum has a :math:`1/f^\chi` property.
        1/f activity is a type of aperiodic activity.

    1/f-like
        Refers to cases in which the activity, or power spectrum, approximates or is similar to a 1/f distribution. In neural data, we often see data which has some aspects of 1/f, but is not formally 1/f, and so we describe this as '1/f-like'.

    Center Frequency (CF)
        The peak frequency of identified peaks.
        The CF is a peak parameter, as part of the periodic component of the data.

    Power (PW)
        The power, over and above the aperiodic component, of identified peaks.
        The PW is a peak parameter, as part of the periodic component of the data.

    Bandwidth (BW)
        The bandwidth of identified peaks.
        The BW is a peak parameter, as part of the periodic component of the data.

    Offset (OFF)
        The y-intercept of the model fit.
        The OFF is an aperiodic parameter, as part of the aperiodic component of the data.

    Knee (KNE)
        An optional parameter of the aperiodic fit that relates to frequency locations where there is a 'bend' or a 'knee', when plotted in log-log space, in the 1/f-like aperiodic activity.
        The KNE is an aperiodic parameter, as part of the aperiodic component of the data.

    Exponent (EXP)
        The exponent of the aperiodic fit, which is :math:`\chi` in the :math:`1/f^\chi` formulation. FOOOF uses and fits exponential functions for the aperiodic fit, whereby :math:`\chi` is equivalent to the slope of a linear fit in log-log space (with a sign flip).
        The EXP is an aperiodic parameter, as part of the aperiodic component of the data.
