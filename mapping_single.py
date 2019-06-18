import http.client
import os
import json
import wget
import mapping_functions
import pprint
import sys

schema = sys.argv[1]
input_file = sys.argv[2]
output_filename = sys.argv[3]

print("\n \n \n MAPPING DOCUMENT: {} \n \n \n".format(input_file))
mapping_functions.map_response(schema, input_file, output_filename + '.elastic.json')


