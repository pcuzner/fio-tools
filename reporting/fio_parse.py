#!/usr/bin/env python

import json
from optparse import OptionParser  # command line option parsing
import os


def get_element_value(json_tree, element_path):

    csr = json_tree
    for elem in element_path.split('/'):
        try:
            csr = csr[elem]
        except:
            csr = 'ERROR_IN_JSON_PATH'
            break
    return csr


def extract_json_data(json_filename):

    json_data = []
    data_ready = False
    last_record = ""
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as raw_json:
            raw_lines = raw_json.readlines()
            start_ptr = 0
            for line in raw_lines:
                if line.startswith('  "client_stats"'):
                    break
                start_ptr += 1
            start_ptr -= 2
            json_data = raw_lines[start_ptr:]
        # with open(json_filename) as raw_json:
        #     for json_in in raw_json:
        #         # when in client server mode the data can have invalid json at the
        #         # start, so we need to bypass invalid lines
        #         if json_in.startswith('{') and last_record.startswith('Disk'):
        #             data_ready = True
        #         if data_ready and json_in[0] in ['{', ' ', '}']:
        #             print json_in[0]
        #             json_data.append(json_in)
        #         else:
        #             last_record = json_in

    return json_data


def get_json_data(json_file, json_path):

    json_data = extract_json_data(json_file)
    status_msg = 'OK'
    response = {}

    if json_data:
        try:
            fio_json = json.loads(''.join(json_data))
        except:
            status_msg = "ERROR: invalid JSON in " % json_file
        else:
            for client_data in fio_json['client_stats']:
                host_name = client_data['hostname']
                element_data = get_element_value(client_data, json_path)
                if str(element_data).startswith('ERROR'):
                    status_msg = "ERROR: unable to find element in json file for path %s" % json_path
                    break
                else:
                    response[host_name] = element_data
    else:
        status_msg = "File name is empty or not usable"

    response['status'] = status_msg

    if __name__ == "__main__":
        print response
    else:
        return response


if __name__ == "__main__":
    DEFAULT_JSON_FILE = '/home/paul/Downloads/test (copy).json'
    DEFAULT_JSON_PATH = 'mixed/clat/percentile/95.000000'

    usage_info = "usage: %prog [options]"

    parser = OptionParser(usage=usage_info, version="%prog 0.1")
    parser.add_option("-f", "--filename", dest="json_file", action="store",
                      help="file name containing fio json")
    parser.add_option("-p", "--path", dest="json_path", action="store",
                      help="element path for the json to extract from the fio json file")

    (options, args) = parser.parse_args()

    input_file = options.json_file if options.json_file else DEFAULT_JSON_FILE
    input_path = options.json_path if options.json_path else DEFAULT_JSON_PATH

    get_json_data(json_file=input_file, json_path=input_path)
