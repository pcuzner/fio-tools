#!/usr/bin/env python

import os
import numpy as np
from optparse import OptionParser

import matplotlib.pyplot as plt
import matplotlib as mpl

import fio_parse

__author__ = 'Paul Cuzner'


# Assumption - the data files we're parsing represent repeated fio runs
# where each run includes another vm's results ie. run1 = 1 job, run 2 = 2
# jobs, etc
# The file names must therefore preserve this order so naming is important
# to ensure the data is read in the correct sequence
#
# must run on a platform with matplotlib and numpy
#

def get_files(path_name):

    file_list = []
    if os.path.isdir(path_name):
        for f in os.listdir(path_name):
            fq_path = os.path.join(path_name, f)
            if os.path.isfile(fq_path):
                # TODO - should add more checking here
                if fq_path[-4:] == '.out':
                    file_list.append(fq_path)
    else:
        if os.path.exists(path_name):
            file_list.append(path_name)
    return sorted(file_list)


def convert_2_ms(x, p=None):
    return "{:3.1f}".format(x/1000)


class ChartDataError(Exception):
    pass


def show_perf_summary(perf_metrics):
    """
    Use the last observation in the dict to provide a quick summary of the
    test run
    :param perf_metrics:(dict) containing the io metrics
    :return:
    """
    read_iops = perf_metrics.get('last_read_iops', [0])
    write_iops = perf_metrics.get('last_write_iops', [0])
    num_reporters = len(perf_metrics.get('read_iops', []))

    all_latency = []
    if sum(perf_metrics.get('last_read_us')) > 0:
        all_latency += perf_metrics.get('last_read_us')
    if sum(perf_metrics.get('last_write_us')) > 0:
        all_latency += perf_metrics.get('last_write_us')

    total_iops = (perf_metrics.get('read_iops')[-1] +
                  perf_metrics.get('write_iops')[-1])

    print("\nSummary Statistics")
    print("\tNumber of Clients  : {}".format(num_reporters))
    print("\tTotal IOPS         : {}".format(total_iops))
    print("\tAVG reads/VM       : {} (std={:3.1f})".format(
        np.mean(read_iops), np.std(perf_metrics['last_read_iops'])))
    print("\tAVG writes/VM      : {} (std={:3.1f})".format(
        np.mean(write_iops), np.std(perf_metrics['last_write_iops'])))

    print("\tAVG. Read Latency  : {}ms".format(
        convert_2_ms(np.mean(perf_metrics.get('last_read_us')))))
    print("\tAVG. Write Latency : {}ms".format(
        convert_2_ms(np.mean(perf_metrics.get('last_write_us')))))
    print("\tAVG. Latency       : {}ms".format(
        convert_2_ms(np.mean(all_latency))))

    print("\nNB.")
    print("- Summary statistics are calculated from the data points in the "
          "final json file \n  (usually the run with the highest vm density)")
    print("- high std dev values indicate inconsistent performance across "
          "vm's\n")



def plot_iops_vs_latency(perf_metrics):
    #
    # Produce the chart and text output of the data

    xloc = np.arange(1, len(perf_metrics['read_iops']) + 1, 1)
    xlabels = ["{} VM's".format(x) for x in xloc if x > 1]
    xlabels.insert(0, '1 VM')

    # Print the data used in the chart to stdout
    micro = u'\u03bc'
    print("\ntitle, {}".format(options.title))
    print("subtitle, {}".format(options.subtitle))
    print("xaxis labels,{}".format(','.join(xlabels)))
    print("read iops,{}".format(
        ','.join(map(str, perf_metrics.get("read_iops")))))
    print("write iops,{}".format(
        ','.join(map(str, perf_metrics.get("write_iops")))))
    print(u"read latency ({}s),{}".format(micro,
          ','.join(map(str, perf_metrics.get("read_latency")))))
    print(u"write latency ({}s),{}\n".format(micro,
          ','.join(map(str, perf_metrics.get("write_latency")))))

    # bar width
    width = 0.4

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.bar(xloc, perf_metrics.get('read_iops'), width, color='#d62728',
            linewidth=0, align='center', label="Read IOPS")
    ax1.bar(xloc, perf_metrics.get('write_iops'), width, color='#1f77b4',
            bottom=perf_metrics.get('read_iops'), linewidth=0, align='center',
            label="Write IOPS")

    ax2.plot(xloc, perf_metrics.get('read_latency'), linewidth=2,
             label="read latency", color='#43a047')
    ax2.plot(xloc, perf_metrics.get('write_latency'), linewidth=2,
             label="write latency", color='#f1a209')

    lines, labels = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()

    ax1.set_ylabel("IOPS")
    ax2.set_ylabel("95%ile Latency (ms)")

    # the latency is in microseconds, so convert the display to ms for
    # readability
    ax2.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(convert_2_ms))

    ax1.legend(lines + lines_2, labels + labels_2, loc='best',
               frameon=False, prop={'size': 10})

    ax1.spines['top'].set_visible(False)    # turn off top border
    ax2.spines['top'].set_visible(False)
    ax1.xaxis.set_ticks_position('bottom')  # turn off top tick marks
    ax1.tick_params(direction='out')        # tick marks on the outside
    ax2.tick_params(direction='out')

    plt.suptitle(options.title, fontsize=14)
    if options.subtitle:
        plt.title(options.subtitle, fontsize=12)
    plt.xticks(xloc, xlabels)
    plt.savefig(options.output_file)
    plt.show()


def main(options):

    # declare a dict to hold summary data.
    perf_data = {'read_iops': [],
                 'last_read_iops': [],
                 'write_iops': [],
                 'last_write_iops': [],
                 'read_latency': [],
                 'last_read_us': [],
                 'write_latency': [],
                 'last_write_us': []
                 }

    json_file_list = get_files(options.fio_file_path)

    mpl.rcParams['figure.facecolor'] = 'white'   # interactive chart
    mpl.rcParams['savefig.facecolor'] = 'white'  # saved chart colour

    if json_file_list:

        last_file = json_file_list[-1]

        for f in json_file_list:

            #
            # Extract the relevant metrics from the json data files
            all = fio_parse.get_json_data(json_file=f,
                                          json_path=['read/iops',
                                                     'read/clat/percentile/95.000000',
                                                     'write/iops',
                                                     'write/clat/percentile/95.000000'])

            if all.get('status', None) == 'OK':

                perf_data['read_iops'].append(
                    sum([int(all['read/iops'].get(vm))
                        for vm in all['read/iops']]))
                perf_data['write_iops'].append(
                    sum([int(all['write/iops'].get(vm))
                        for vm in all['write/iops']]))
                perf_data['read_latency'].append(
                    int(np.mean([all['read/clat/percentile/95.000000'].get(vm)
                        for vm in all['read/clat/percentile/95.000000']])))
                perf_data['write_latency'].append(
                    int(np.mean([all['write/clat/percentile/95.000000'].get(vm)
                        for vm in all['write/clat/percentile/95.000000']])))

                if f == last_file:
                    # we'll produce a final summary specifically from the last
                    # json file's data (should be the json file from fio run
                    # with the most reporters (vm's)
                    perf_data['last_read_iops'] = [int(
                        all['read/iops'].get(vm)) for vm in all['read/iops']]
                    perf_data['last_write_iops'] = [int(
                        all['write/iops'].get(vm)) for vm in all['write/iops']]
                    perf_data['last_read_us'] = [int(
                        all['read/clat/percentile/95.000000'].get(vm))
                                                 for vm in all['read/clat/percentile/95.000000']]
                    perf_data['last_write_us'] = [int(
                        all['write/clat/percentile/95.000000'].get(vm))
                                                 for vm in all['write/clat/percentile/95.000000']]
                    pass

            else:
                # problem reading the data from the json file(s)
                raise ChartDataError("Problem reading the json files. Did you "
                                     "have unified_rw_reporting=1 set in your"
                                     " fio jobfile?")
        if len(json_file_list) > 1:
            # Producing a chart only really makes sense when there are multiple
            # json files providing multiple data points
            plot_iops_vs_latency(perf_data)

        # Summarise the data provided by the last json file in the archive
        show_perf_summary(perf_data)


    else:
        print("no files found matching the path"
              " provided {}".format(options.fio_file_path))


if __name__ == "__main__":
    usage_info = "Usage: %prog [options]"

    parser = OptionParser(usage=usage_info, version="%prog 0.1")

    parser.add_option("-D", "--debug", dest="debug", action="store_true",
                      default=False,
                      help="turn on debug output")
    parser.add_option("-p", "--pathname", dest="fio_file_path", action="store",
                      help="file name/path containing fio json output")

    parser.add_option("-t", "--title", dest="title", action="store",
                      help="Chart title", default="FIO Chart")
    parser.add_option("-s", "--subtitle", dest="subtitle", action="store",
                      help="Chart subtitle", default=None)

    parser.add_option("-o", "--output", dest="output_file",action="store",
                      help="output filename", default="myfile.png")

    (options, args) = parser.parse_args()

    if options.fio_file_path:
        main(options)
    else:
        print("You must provide a path or filename for the fio json file(s)")
