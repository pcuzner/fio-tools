#!/usr/bin/env python

__author__ = 'paul'
import fio_parse
from optparse import OptionParser
import os
from fio_plot import FIOPlot

# Assumption - the data files we're parsing represent repeated fio runs where each run
# includes another vm's results ie. run1 = 1 job, run 2 = 2 jobs, etc
# the file names must therefore preserve this order so naming is important to ensure the
# data is read in the correct sequence
#
# must run on a platform with matplotlib to allow the chart to be generated - which requires
# an x server to also be installed
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


def get_max_listsize(data_in):
    return max((len(obs_list)) for key, obs_list in data_in.iteritems())


def format_perf_data(perf_data):

    max_size = get_max_listsize(perf_data)
    for key in perf_data:
        obs_list = perf_data[key]
        if len(obs_list) < max_size:
            padding = [None]*(max_size - len(obs_list))
            perf_data[key] = padding + obs_list

    return perf_data

def aggregate_data(data_in, aggr_type='iops'):
    aggr_data = {}
    summary_data = []
    max_element = get_max_listsize(data_in)

    for ptr in range(0,max_element):
        data_points = []
        divisor = 0
        for key in data_in:
            if data_in[key][ptr] is not None:
                data_points.append(data_in[key][ptr])
                divisor +=1 
        if aggr_type == 'iops':
            summary_data.append(sum(data_points))
        elif aggr_type == 'latency':
            print "%d " % (sum(data_points)/float(divisor))
            summary_data.append(sum(data_points)/float(divisor))

    aggr_data['Aggregated Data'] = summary_data
    return aggr_data

def main(options):

    perf_data = {}

    chart_ceiling = None if options.ceiling == "none" else options.ceiling

    json_file_list = get_files(options.fio_file_path)

    if json_file_list:
        for f in json_file_list:
            perf_sample = fio_parse.get_json_data(json_file=f, json_path=options.json_key)
            if perf_sample['status'] == 'OK':
                del perf_sample['status']
                for key in perf_sample:
                    if key in perf_data:
                        perf_data[key].append(perf_sample[key])
                    else:
                        perf_data[key] = [perf_sample[key]]

        # need to add padding to the data to make each entry have the same 
        # number of observations
        fmtd_data = format_perf_data(perf_data)

        if options.data_aggregate:
            fmtd_data = aggregate_data(fmtd_data, options.chart_type)

        chart = FIOPlot(chart_type=options.chart_type,
                        data=fmtd_data,
                        title=options.title,
                        ceiling=chart_ceiling,
                        xlabel='Concurrent jobs',
                        ylabel=options.ylabel)

        chart.generate_plot(options.output_file)

        print fmtd_data
    else:
        print "no files found matching the path provided %s" % options.fio_file_path


if __name__ == "__main__":
    usage_info = "Usage: %prog [options]"

    parser = OptionParser(usage=usage_info, version="%prog 0.1")
    parser.add_option("-y", "--yaxis-label", dest="ylabel", action="store",
                      default="Response Time (ms)",
                      help="Chart label for the yaxis")
    parser.add_option("-T", "--chart-type", dest="chart_type", action="store",
                      choices=['iops','latency'],default='latency',
                      help="chart type - either iops or [latency]")
    parser.add_option("-a", "--aggr", dest="data_aggregate", action="store_true",
                      default=False,
                      help="aggregate the iops or latency data, instead of per job data")
    parser.add_option("-D", "--debug", dest="debug", action="store_true",
                      default=False,
                      help="turn on debug output")
    parser.add_option("-c", "--ceiling", dest="ceiling", action="store",
                      default=50000,
                      help="(int) ceiling to show Max acceptable values, or none")
    parser.add_option("-p", "--pathname", dest="fio_file_path", action="store",
                      help="file name/path containing fio json output")
    parser.add_option("-k", "--keyname", dest="json_key", action="store",
                      help="json path for the attribute to extract from the fio json file(s)")
    parser.add_option("-t", "--title", dest="title", action="store",
                      help="Chart title", default="FIO Chart")
    parser.add_option("-o", "--output", dest="output_file",action="store",
                      help="output filename", default="myfile.png")

    (options, args) = parser.parse_args()

    if options.fio_file_path and options.json_key:
        main(options)
    else:
        print "You must provide a path or filename for the fio json file(s)"
