# -*- coding: utf-8 -*-

import json
import xmltodict
import os
import pprint

def expand_path(path):
    """
    Function to expand a path string of the type:
    'TEI.teiHeader.fileDesc.titleStmt.title'
    and to return a path list of the type:
    ['TEI', 'teiHeader', 'fileDesc', 'titleStmt', 'title']
    :param path: string of nested dictionaries separated by '.'
    :return: list of strings, where each element is a dictionary
    """
    return path.split(".")


def find_path(path, diz):
    """
    Function iteratively going deeper into a nested dictionary,
    up to a value which is not a dictionary (but could be a list).
    If no element is found, because the key is missing, the function
    exit from the loop (further nested keys will be missing too)
    and returns NONE
    :param path: path string of the type:
                'TEI.teiHeader.fileDesc.titleStmt.title
    :param diz: the dictionary to access
    :return: the value of the most nested dictionary, or None
    """
    expanded_path = expand_path(path)
    #print("\n expanded path :{}".format(expanded_path))
    for pos in expanded_path:
        #print("pos", pos)
	if diz is None:
            print("found a None element in {}. This entry will be not reported in the JSON.".format(pos))
            break
        if isinstance(diz, dict):
            diz = diz.get(pos)
        else:
            print("{} is not a dictionary".format(diz))
            diz = diz.get(pos)
    #print("diz", diz)
    return diz


def read_response(file):
    if os.path.splitext(file)[1] == ".json":
        resp = json2dict(file)
    elif os.path.splitext(file)[1] == ".xml":
        resp = xml2dict(file)
    return resp



def json2dict(file):
    """
    Function to read a json file and parse it do a dictionary
    :param file: json file
    :return: the dictionary
    """
    with open(file, "r", encoding='utf-8') as read_file:
        # encoding='utf-8' to take into account Greek letters
        d = json.load(read_file, encoding='utf-8')
    return d


def xml2dict(file):
    """
    Function to read a xml file and parse it do a dictionary
    :param file: xml file
    :return: the dictionary
    """
    with open(file, "r", encoding='utf-8') as read_file:
        # encoding='utf-8' to take into account Greek letters
        d = xmltodict.parse(read_file.read(), encoding='utf-8')
        # the output is an OrderedDict
        # to convert OrderedDict to a regular Dict:
        d = json.loads(json.dumps(d))
    return d


def dict2json(d, file):
    """
    Function to write a json file parsing the dictionary,
    ready to be indexed in Elasticsearch
    :param d: dictionary to be converted to json
    :param file: file json to be created and written
    """
    with open(file, 'w', encoding='utf-8') as j:
        # ensure_ascii=False to take into account Greek letters
        json.dump(d, j, indent=2, ensure_ascii=False)


def list2dict(flat_list):
    """
    Function taking a list of (key, value) tuples,
    where the value can be a nested path like:
    ('title.path', 'Titel')
    and transform it into a dictionary like:
    {"title":{"path":"Titel"}}
    :param flat_list: list of (key, value) tuples
    :return: the dictionary
    """
    output_dict = {}
    for key, value in flat_list:
        key_levels = key.split('.')
        current_dict = output_dict
        if len(key_levels) == 1:
            if key_levels[0] not in current_dict:
                current_dict[key_levels[0]] = value
        else:
            for level_name in key_levels[:-1]:
                if level_name not in current_dict:
                    current_dict[level_name] = {}
                current_dict = current_dict[level_name]

            current_dict[key_levels[-1]] = value

    return output_dict


def __dict2list(v, resp, prefix, append_to):
    """
    Hidden function to flatten a nested dictionary into a list of tuples.
    :param v: the dictionary with the schema
    :param resp: the dictionary with the response
    :param prefix: the prefix of the path. usually empty at the beginning
    :param append_to: the list where to append (defined in the external function)
    """
    if isinstance(v, dict):
        for k, v2 in v.items():
            p2 = "{}{}.".format(prefix, k)
            __dict2list(v2, resp, p2, append_to)

    elif isinstance(v, list):
        for i, v2 in enumerate(v):
            p2 = "{}{}.".format(prefix, i)
            __dict2list(v2, resp, p2, append_to)

    else:
        newprefix = prefix.rstrip('.')
        leeve = (newprefix, v)
        if os.path.splitext(newprefix)[1].lstrip('.') == "path":
            #print("leeve con path ", leeve)
            value = find_path(v, resp)
            # skip the mapping of missing key:value pairs in the response
            if value is not None:
                casted_value = cast_to_string(value)
            #print("value", value, type(value))
            #print("casted value",casted_value, type(casted_value))
                output = (os.path.splitext(newprefix)[0], casted_value)
                #print("output", output)
                append_to.append(output)


def dict2list(v, v2, prefix=''):
    """
    Function to flatten a nested dictionary into a list of tuples.
    :param v: the dictionary with the schema
    :param v2: the dictionary with the response
    :param prefix: the prefix of the path. usually empty at the beginning
    :return: the flattened list of the dictionary
    """
    dictList = []
    __dict2list(v, v2, prefix, dictList)
    return dictList


def cast_to_string(elem):
    if isinstance(elem, dict):
        #print("WARNING: Unexpected dictionary. Please check. Casting {} to string".format(elem))
        elem = str(elem)

    elif isinstance(elem, list):
        for i in range(len(elem)):
            if not isinstance(elem[i], str):
                #print("WARNING: Casting element {} of list {} to string because it was {}".format(elem[i],
                #                                                                                  elem,
                #                                                                                  type(elem[i])))
                elem[i] = str(elem[i])
    else:
        # assuming that if not a list, can only be a single element
        if not isinstance(elem, str):
            #print("WARNING: Casting {} to string because it was {}".format(elem, type(elem)))
            elem = str(elem)

    return elem


def map_response(schema_file, response_file, elastic_response_file):
    schema = json2dict(schema_file)
    response = read_response(response_file)
    flat_response = dict2list(schema["properties"], response)
    dictionary = list2dict(flat_response)
    dict2json(dictionary, elastic_response_file)
