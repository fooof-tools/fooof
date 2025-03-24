"""Utilities for object functionality - including running in parallel & progress bars."""

from functools import partial
from multiprocessing import Pool, cpu_count

from specparam.modutils.dependencies import safe_import

###################################################################################################
## PARALLEL

def run_parallel(pfunc, data, n_jobs, progress):
    """Run model fitting in parallel.

    Parameters
    ----------
    pfunc : callable
        Partialized function to apply to data.
    data : array
        The data to operate across.
    n_jobs : int, optional, default: 1
        Number of jobs to run in parallel.
        1 is no parallelization. -1 uses all available cores.
    progress : {None, 'tqdm', 'tqdm.notebook'}, optional
        Which kind of progress bar to use. If None, no progress bar is used.

    Returns
    -------
    results : list
        Results from running model fitting in parallel.
    """

    n_jobs = cpu_count() if n_jobs == -1 else n_jobs
    with Pool(processes=n_jobs) as pool:
        results = list(pbar(pool.imap(pfunc, data), progress, len(data)))

    return results

## GROUP

def run_parallel_group(model, data, n_jobs, progress):
    """Wrapper function for running in parallel - group model."""

    pfunc = partial(_par_fit_group, group=model)

    return run_parallel(pfunc, data, n_jobs, progress)


def _par_fit_group(power_spectrum, group):
    """Function to partialize for running in parallel - group."""

    group._pass_through_spectrum(power_spectrum)
    group.algorithm._fit()

    return group.results._get_results()

## EVENT

def run_parallel_event(model, data, n_jobs, progress):
    """Wrapper function for running in parallel - event model."""

    pfunc = partial(_par_fit_event, model=model)

    return run_parallel(pfunc, data, n_jobs, progress)


def _par_fit_event(spectrogram, model):
    """Function to partialize for running in parallel - event."""

    model.data.power_spectra = spectrogram.T
    model.fit()

    return model.results.get_results()

###################################################################################################
## PROGRESS BARS

def pbar(iterable, progress, n_to_run):
    """Add a progress bar to an iterable to be processed.

    Parameters
    ----------
    iterable : list or iterable
        Iterable object to potentially apply progress tracking to.
    progress : {None, 'tqdm', 'tqdm.notebook'}
        Which kind of progress bar to use. If None, no progress bar is used.
    n_to_run : int
        Number of jobs to complete.

    Returns
    -------
    progress_bar : iterable or tqdm object
        Iterable object, with tqdm progress functionality, if requested.

    Raises
    ------
    ValueError
        If the input for `progress` is not understood.

    Notes
    -----
    The explicit `n_to_run` input is required as tqdm requires this in the parallel case.
    The `tqdm` object that is potentially returned acts the same as the underlying iterable,
    with the addition of printing out progress every time items are requested.
    """

    # Check progress specifier is okay
    tqdm_options = ['tqdm', 'tqdm.notebook']
    if progress is not None and progress not in tqdm_options:
        raise ValueError("Progress bar option not understood.")

    # Set the display text for the progress bar
    desc = 'Running specparam'

    # Use a tqdm, progress bar, if requested
    if progress:

        # Try loading the tqdm module
        tqdm = safe_import(progress)

        if not tqdm:

            # If tqdm isn't available, proceed without a progress bar
            print(("A progress bar requiring the 'tqdm' module was requested, "
                   "but 'tqdm' is not installed. \nProceeding without using a progress bar."))
            progress_bar = iterable

        else:

            # If tqdm loaded, apply the progress bar to the iterable
            progress_bar = tqdm.tqdm(iterable, desc=desc, total=n_to_run, dynamic_ncols=True)

    # If progress is None, return the original iterable without a progress bar applied
    else:
        progress_bar = iterable

    return progress_bar
