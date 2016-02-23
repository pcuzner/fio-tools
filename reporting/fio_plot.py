__author__ = 'paul'

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def convert_2_ms(x, p):
    return "%d" % (x/1000)
    
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
        plt.ylim(ymin=0,ymax=150000)
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
        # ax.yaxis.set_ticks(np.arange(0,150000,10000))
        plt.tick_params(axis='x', top='off')
        plt.tick_params(axis='y', right='off')
        #ax.yaxis.set_ticks_position('left')
        #ax.xaxis.set_ticks_position('bottom')
        ax.tick_params(direction='out')
                
        major_tick = mpl.ticker.MultipleLocator(10000)
        #major_fmt = mpl.ticker.FormatStrFormatter('%d')
        #minor_tick = mpl.ticker.MultipleLocator(10000)
        ax.yaxis.set_major_locator(major_tick)
        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(convert_2_ms))

        #ax.yaxis.set_minor_locator(minor_tick)
        #ax.yaxis.set_minor_formatter(mpl.ticker.FuncFormatter(convert_2_ms))
        #ax.yaxis.grid(True, which='minor')
        

        
        plt.ylabel(self.ylabel)
        plt.xlabel(self.xlabel)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
        plt.grid()
        plt.savefig(filename)

