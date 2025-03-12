"""Utility functions & decorators for the module."""

from copy import deepcopy

###################################################################################################
###################################################################################################

## DATA

DOCSTRING_SECTIONS = ['Parameters', 'Returns', 'Yields', 'Raises',
                      'Warns', 'Examples', 'References', 'Notes',
                      'Attributes', 'Methods']

## FUNCTIONS

def get_docs_indices(docstring, sections=DOCSTRING_SECTIONS):
    """Get the indices of each section within a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to check indices for.
    sections : list of str, optional
        List of sections to check and get indices for.
        If not provided, uses the default set of

    Returns
    -------
    inds : dict
        Dictionary in which each key is a section label, and each value is the corresponding index.
    """

    inds = {label : None for label in sections}

    for ind, line in enumerate(docstring.split('\n')):
        for key in inds:
            if key in line:
                inds[key] = ind

    return inds


def docs_drop_param(docstring):
    """Drop the first parameter description for a string representation of a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to drop first parameter from.

    Returns
    -------
    str
        New docstring, with first parameter dropped.

    Notes
    -----
    This function assumes numpy docs standards.
    It also assumes the parameter description to be dropped is only 2 lines long.
    """

    sep = '----------\n'
    ind = docstring.find(sep) + len(sep)
    front, back = docstring[:ind], docstring[ind:]

    for _ in range(2):
        back = back[back.find('\n')+1:]

    return front + back


def docs_replace_param(docstring, replace, new_param):
    """Replace a parameter description in a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to replace parameter description within.
    replace : str
        The name of the parameter to switch out.
    new_param : str
        The new parameter description to replace into the docstring.
        This should be a string structured to be copied directly into the docstring.

    Returns
    -------
    new_docstring : str
        Update docstring, with parameter switched out.
    """

    # Take a copy to make sure to avoid any potential aliasing
    docstring = deepcopy(docstring)

    # Find the index where the param to replace is
    p_ind = docstring.find(replace)

    # Find the second newline (end of to-replace param)
    ti = docstring[p_ind:].find('\n')
    n_ind = docstring[p_ind + ti + 1:].find('\n')
    end_ind = p_ind + ti + 1 + n_ind

    # Reconstitute docstring, replacing specified parameter
    new_docstring = docstring[:p_ind] + new_param + docstring[end_ind:]

    return new_docstring


def docs_append_to_section(docstring, section, add):
    """Append extra information to a specified section of a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to update.
    section : str
        Name of the section within the docstring to add to.
    add : str
        Text to append to specified section of the docstring.

    Returns
    -------
    str
        Updated docstring.

    Notes
    -----
    This function assumes numpydoc documentation standard.
    """

    return '\n\n'.join([split + add if section in split else split \
                        for split in docstring.split('\n\n')])


def docs_get_section(docstring, section, output='extract', end=None):
    """Extract and/or remove a specified section from a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to extract / remove a section from.
    section : str
        Label of the section to extract / remove.
    mode : {'extract', 'remove'}
        Run mode, options:
            'extract' - returns the extracted section from the docstring.
            'remove' - returns the docstring after removing the specified section.
    end : str, optional
        Indicates the contents of a line that signals the end of the section to select.
        If not provided, the section is selected until a blank line.

    Returns
    -------
    out_docstring : str
        Extracted / updated docstring.
    """

    outs = []
    in_section = False

    docstring_split = docstring.split('\n')
    for ind, line in enumerate(docstring_split):

        # Track whether in the desired section
        if section in line and '--' in docstring_split[ind + 1]:
            in_section = True
        if end:
            if in_section and '    ' + end == line:
                in_section = False
                # In this approach, an extra newline is caught - so pop it off
                outs.pop()
        elif in_section and line == '':
            in_section = False

        # Collect desired outputs based on whether extracting or removing section
        if output == 'extract' and in_section:
            outs.append(line)
        if output == 'remove' and not in_section:
            outs.append(line)

        # As a special case, when removing section, end section marker if there is a '%' line
        if in_section and output == 'remove' and not line.isspace() and line.strip()[0] == '%':
            in_section = False

    out_docstring = '\n'.join(outs)

    return out_docstring


def docs_add_section(docstring, section):
    """Add a section to a specified index of a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to add section to.
    section : str
        New section to add to docstring.

    Returns
    -------
    out_docstring : str
        Updated docstring, with the new section added.
    """

    inds = get_docs_indices(docstring)

    # Split the section, extract the label, and check it's a known docstring section
    split_section = section.split('\n')
    section_label = split_section[0].strip()
    assert section_label in inds, 'Section label does not match expected list.'

    # Remove the header section from the docstring (to replace it)
    docstring = docs_get_section(docstring, section_label, 'remove')

    # Check for and drop leading and trailing empty lines
    split_section = split_section[1:] if split_section[0] == '' else split_section
    split_section = split_section[:-1] if split_section[-1] == '    ' else split_section

    # Insert the new section into the docstring and rejoin it together
    split_docstring = docstring.split('\n')
    split_docstring[inds[section_label]:inds[section_label]] = split_section
    new_docstring = '\n'.join(split_docstring)

    return new_docstring


def copy_doc_func_to_method(source):
    """Decorator that copies method docstring from function, dropping first parameter.

    Parameters
    ----------
    source : function
        Source function to copy docstring from.

    Returns
    -------
    wrapper : function
        The decorated function, with updated docs.
    """

    def wrapper(func):

        func.__doc__ = docs_drop_param(source.__doc__)

        return func

    return wrapper


def copy_doc_class(source, section='Attributes', add=''):
    """Decorator that copies method docstring from class, to another class, adding extra info.

    Parameters
    ----------
    source : cls
        Source class to copy docstring from.
    section : str, optional, default: 'Attributes'
        Name of the section within the docstring to add to.
     add : str, optional
        Text to append to specified section of the docstring.

    Returns
    -------
    wrapper : cls
        The decorated class, with updated docs.
    """

    def wrapper(func):

        func.__doc__ = docs_append_to_section(source.__doc__, section, add)

        return func

    return wrapper


def replace_docstring_sections(replacements):
    """Decorator to drop in docstring sections

    Parameters
    ----------
    replacements : str or list of str
        Section(s) to drop into the decorated function's docstring.
    """

    def wrapper(func):

        docstring = func.__doc__

        for replacement in [replacements] if isinstance(replacements, str) else replacements:
            docstring = docs_add_section(docstring, replacement)

        func.__doc__ = docstring

        return func

    return wrapper
