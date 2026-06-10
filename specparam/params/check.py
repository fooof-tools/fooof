"""Functionality to check available parameter conversions."""

###################################################################################################
###################################################################################################

def check_converters(component):
    """Check the set of parameter converters that are available.

    Parameters
    ----------
    component : {'aperiodic', 'periodic'}
        Which component to check available parameter converters for.
    """

    from specparam.params.definitions import CONVERTERS

    print('Available {:s} converters:'.format(component))
    for param, convs in CONVERTERS[component].items():
        print(param)
        for label, converter in convs.items():
            print('    {:10s}    {:s}'.format(converter.name, converter.description))
