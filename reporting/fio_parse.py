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

    return json_data


class JSONError(Exception):
    pass


def get_json_data(json_file, json_path):
    """ return a dict containing the required values from the json file

    :param json_file: (str) file name containing the fio output in JSON format
    :param json_path: (str or list) to the relevant json element delimeted by
                      '/'
                      e.g. read/iops or ['read/iops','write/iops']
    :return: dict containing one element per json key, with all values for
             that key. A 'status' element is also added to denote the
             success of the JSON extract ('OK' or Error bla bla)
    """

    print 'processing file %s' % json_file

    json_data = extract_json_data(json_file)
    json_key_list = []

    if isinstance(json_path, list):
        json_key_list = json_path
    else:
        json_key_list.append(json_path)

    response = {_k: {} for _k in json_key_list}
    response['status'] = 'OK'

    if json_data:
        try:
            fio_json = json.loads(''.join(json_data))
        except:
            response['status'] = "ERROR: invalid JSON in {}".format(json_file)
        else:
            try:

                missing_keys = []

                for client_data in fio_json['client_stats']:
                    host_name = client_data['hostname']

                    for json_key in json_key_list:
                        element_data = get_element_value(client_data, json_key)

                        if str(element_data).startswith('ERROR'):
                            missing_keys.append(json_key)
                            print("Warning: looking for json path '{}' but can't find it, skipping".format(json_key))
                            continue

                        kv = {host_name: element_data}
                        response[json_key].update(kv)

                    # remove any missing keys from the candidate key list
                    json_key_list = [key for key in json_key_list
                                     if key not in missing_keys]

            except JSONError as err_text:
                response['status'] = err_text

    else:
        response['status'] = "ERROR: File name is empty or not usable"



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
