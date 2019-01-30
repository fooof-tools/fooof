FOOOF Glossary
==============

.. glossary::

    FOOOF
        FOOOF stands for 'fitting oscillations & one-over f'.

    Periodic
        Rhythmic component(s) of the signal, that reflect putative oscillations.

    Aperiodic
        Arrhythmic components of the signal, reflecting 1/f like activity.

    Peaks
        Locations in the power spectrum that are identified to have power over and above the aperiodic component, and are thus modelled as 'peaks', reflecting putative oscillations.

    Center Frequency
        The peak frequency of identified peaks.

    Amplitude
        The amplitude, over and above the aperiodic component, of identified peaks.

    Bandwidth
        The bandwidth of identified peaks.

    Offset
        The y-intercept of the model fit.

    Knee
        An optional parameter of the aperiodic fit that relates to frequency locations at where there is a 'bend' or a 'knee', when plotted in log-log space, in the 1/f-like aperiodic activity.

    Exponent
        The exponent of the aperiodic fit, which is :math:`\chi` in the :math:`1/f^\chi` formulation. FOOOF uses and fits exponential functions for the aperiodic fit, whereby :math:`\chi` is equivalent to the slope of a linear fit in log-log space (with a sign flip).
