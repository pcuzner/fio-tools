__author__ = 'paul'

# todo


import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from textwrap import wrap

def convert_2_ms(x, p):
    return "%d" % (x/1000)
    
class FIOPlot(object):

    def __init__(self, chart_type, data, ceiling=50000, title='', xlabel='', ylabel=''):

        mpl.rcParams['figure.facecolor'] = 'white'      # interactive chart
        mpl.rcParams['savefig.facecolor'] = 'white'     # saved chart colour
        self.chart_type=chart_type
        self.dataset = data                     # dict expected from the caller
        #self.num_entries = self.__get_max_size()
        self.num_entries = len(data)
        # print "number of entries in the dataset is %d " % self.num_entries
        if 'Aggregated Data' in self.dataset:
            # aggregated data received, so define the xaxis by the number of entries
            self.xseries = range(1, (len(self.dataset['Aggregated Data']) + 1), 1)
        else:
            self.xseries = range(1, (self.num_entries + 1), 1)

        if ceiling is not None:
            self.dataset['Ceiling'] = [ceiling]*len(self.xseries)

        # print "xseries set to %s" % self.xseries
        self.title = "\n".join(wrap(title, 60))
        self.xlabel = xlabel
        self.ylabel = ylabel

    #def __get_max_size(self):
    #    return max((len(obs_list)) for key, obs_list in self.dataset.iteritems())

    def generate_plot(self, filename):
        fig, ax = plt.subplots()

        # num_cols defines the no. columns in the legend. matplotlib will split the legend
        # entries across this number of columns as evenly as possible
        num_cols = (len(self.dataset) // 16) + 1

        # determine the max y axis value by looking at the data
        y_values = []
        for key in self.dataset:
            if key is not "Ceiling":
                y_values += self.dataset[key]

        y_maximum = max(y_values)*1.2 

        plt.ylim(0,y_maximum)

        fig.set_size_inches(13, 8)
        if self.num_entries > 20:
            x_major = np.arange(0,len(self.dataset)+1,5)
        else:
            #x_major = np.arange(0,len(self.dataset)+1,1)
            x_major = self.xseries
        
        # replace the first label since our data series starts at 1 i.e. 1 job
        x_major[0] = 1
        x_minor = np.arange(0,len(self.dataset),1)

        ax.set_xticks(x_major)
        ax.set_xticks(x_minor,minor=True)
        ax.get_xaxis().set_tick_params(which='both', direction='out')
        ax.grid(which='minor', alpha=0.5)       # minor grid more faint than major grid

        plot_color = iter(plt.cm.Set1(np.linspace(0, 1, len(self.xseries) + 1)))
        for key in sorted(self.dataset):
            c = next(plot_color)
            lwidth = 1
            plot_marker = None
            lstyle = 'solid'
            if key.startswith('Ceiling'):
                lwidth = 2
                lstyle = 'dashed'
                c = 'r'
            elif key.startswith('Aggregated'):
                plot_marker = '.'
                c='b'

            ax.plot(self.xseries, 
                    self.dataset[key], 
                    ls=lstyle, 
                    marker=plot_marker, 
                    markersize=10, 
                    c=c, 
                    linewidth=lwidth, 
                    label=key)

        plt.title(self.title)
        
        plt.tick_params(axis='x', which='both', bottom='on', top='off', labelbottom='on')
        plt.tick_params(axis='y', right='off',direction='out',which='both')
                
        if self.chart_type == 'latency':
            # latency data is provided in usec, so we need to convert to ms

            ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(convert_2_ms))
            if y_maximum < 10000:
                ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(200))
            #y_interval = int(y_maximum/10) - (int(y_maximum/10) % 1000)
            #y_major = np.arange(0,y_maximum,y_interval)
            #y_minor = np.arange(0,y_maximum, int(y_interval/5))

            #ax.set_yticks(y_major)
            #ax.set_yticks(y_minor,minor=True)
        else:
            pass

        
        plt.ylabel(self.ylabel)
        plt.xlabel(self.xlabel)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=num_cols, frameon=False)

        # set the font size in the legend to 10
        plt.setp(plt.gca().get_legend().get_texts(), fontsize='10')
        plt.grid()                          # show the grid
        plt.savefig(filename)               # save the graph to a file

