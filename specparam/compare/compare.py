"""   """

from copy import deepcopy

from specparam.plts.compare import plot_comparison
from specparam.reports.strings import gen_model_comparison_str

###################################################################################################
###################################################################################################

class ModelComparison():
    """   """

    def __init__(self, models=None):
        """   """

        self.models = []
        self.add_models(models)

    def fit(self, freqs=None, data=None, freq_range=None, prechecks=True):
        """   """

        self.models[0].fit(freqs, data, freq_range)
        for model in self.models[1:]:
            model.fit(prechecks=False)

    def report(self, freqs=None, data=None, freq_range=None, prechecks=True):
        """   """

        self.fit(freqs, data, freq_range, prechecks)
        self.print()
        self.plot()

    def add_models(self, models, clear=False):
        """   """

        for model in models:
            self.models.append(deepcopy(model))

        if self.models:
            self.data = deepcopy(models[0].data)
            for model in self.models:
                model.data = self.data

    def plot(self):
        """   """

        plot_comparison(self)

    def print(self):
        """   """

        print(gen_model_comparison_str(self))
