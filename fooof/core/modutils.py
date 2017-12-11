"""Utility functions for dealing with FOOOF, as a module."""

###################################################################################################
###################################################################################################

def get_obj_desc():
    """Get dictionary specifying FOOOF object names and kind of attributes."""

    attributes = {'results' : ['background_params_', 'oscillation_params_', 'error_', 'r2_',
                               '_gaussian_params', 'freq_range', 'freq_res'],
                  'settings' : ['amp_std_thresh', 'bandwidth_limits', 'bg_use_knee',
                                'max_n_oscs', 'min_amp'],
                  'dat' : ['psd', 'freq_range', 'freq_res'],
                  'hidden_settings' : ['_bg_fit_func', '_std_limits', '_bg_bounds'],
                  'arrays' : ['freqs', 'psd', 'background_params_', 'oscillation_params_',
                              '_gaussian_params'],
                  'alias_funcs' : ['plot', 'save', 'create_report']}
    attributes['all_settings'] = attributes['settings'] + attributes['hidden_settings']

    return attributes


def docs_drop_param(ds):
    """Drop the first parameter description for a string representation of a docstring.

    Parameters
    ----------
    ds : str
        Docstring to drop first parameter from.
    """

    tm = '----------\n'
    ind = ds.find(tm) + len(tm)
    fr, ba = ds[:ind], ds[ind:]

    for i in range(2):
        ba = ba[ba.find('\n')+1:]

    return fr + ba
