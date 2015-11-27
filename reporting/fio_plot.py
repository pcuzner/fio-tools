__author__ = 'paul'

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


class FIOPlot(object):

    def __init__(self, data, latency_ceiling=50000, title='', xlabel='', ylabel=''):
        # set defaults for the figure facecolor in the interactive window and saved files to white
        mpl.rcParams['figure.facecolor'] = 'white'
        mpl.rcParams['savefig.facecolor'] = 'white'
        self.dataset = data  # dict expected
        num_entries = self.__get_max_size()
        self.dataset['Latency Ceiling'] = [latency_ceiling]*num_entries
        self.xseries = range(1, (num_entries + 1), 1)
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def __get_max_size(self):
        return max((len(obs_list)) for key, obs_list in self.dataset.iteritems())

    def generate_plot(self, filename):
        fig, ax = plt.subplots()
        fig.set_size_inches(13, 8)

        plot_color = iter(plt.cm.Set1(np.linspace(0, 1, len(self.xseries) + 1)))
        for key in sorted(self.dataset):
            c = next(plot_color)
            lwidth = 1
            if key.startswith('Latency'):
                lwidth = 2
                c = 'r'
            ax.plot(self.xseries, self.dataset[key], c=c, linewidth=lwidth, label=key)

        plt.title(self.title)
        # self.xticks(x, xtickmarks)
        plt.ylabel(self.ylabel)
        plt.xlabel(self.xlabel)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        plt.savefig(filename)

