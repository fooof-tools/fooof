"""Utilities for debugging."""

import sys
import platform

###################################################################################################
###################################################################################################

def sys_info():
    """Print out system information."""

    ljust = 15

    out = 'SYSTEM \n'
    out += 'Platform:'.ljust(ljust) + platform.platform() + '\n'

    out += '\nPYTHON \n'
    out += 'Version:'.ljust(ljust) + str(sys.version).replace('\n', ' ') + '\n'
    out += 'Executable:'.ljust(ljust) + sys.executable + '\n'

    out += '\nMODULES \n'
    for mod_name in ('numpy', 'scipy', 'matplotlib'):
        out += ('%s:' % mod_name).ljust(ljust)
        try:
            mod = __import__(mod_name)
            version = mod.__version__
        except Exception:
            out += 'Not found\n'
        out += '%s\n' % (version)

    print(out, end='')
