"""Style and aesthetics definitions for plots."""

###################################################################################################
###################################################################################################

def check_n_style(style_func, *args):
    """"Check if a style function has been passed, and apply it to a plot if so.

    Parameters
    ----------
    style_func : callable or None
        Function to apply styling to a plot axis.
    *args
        Inputs to the style plot.
    """

    if style_func:
        style_func(*args)


def style_spectrum_plot(ax, log_freqs, log_powers):
    """Apply style and aesthetics to a power spectrum plot.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply styling to.
    log_freqs : bool
        Whether the frequency axis is plotted in log space.
    log_powers : bool
        Whether the power axis is plotted in log space.
    """

    # Get labels, based on log status
    xlabel = 'Frequency' if not log_freqs else 'log(Frequency)'
    ylabel = 'Power' if not log_powers else 'log(Power)'

    # Aesthetics and axis labels
    ax.set_xlabel(xlabel, fontsize=20)
    ax.set_ylabel(ylabel, fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.grid(True)

    # If labels were provided, add a legend
    if ax.get_legend_handles_labels()[0]:
        ax.legend(prop={'size': 16}, loc='upper right')


def style_param_plot(ax):
    """Apply style and aesthetics to a peaks plot.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply styling to.
    """

    # Set the top and right side frame & ticks off
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Set linewidth of remaining spines
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    # Aesthetics and axis labels
    for item in ([ax.xaxis.label, ax.yaxis.label]):
        item.set_fontsize(20)
    ax.tick_params(axis='both', which='major', labelsize=16)

    # If labels were provided, add a legend and standardize the dot size
    if ax.get_legend_handles_labels()[0]:
        legend = ax.legend(prop={'size': 16})
        for handle in legend.legendHandles:
            handle._sizes = [100]
