import http.client
import os
import json
import wget
import mapping_functions
import pprint
import sys

schema = sys.argv[1]
input_folder = sys.argv[2]
output_folder = sys.argv[3]

#schema = "schema-for-json-response.json" 
#input_folder = "./episteme/" 
#output_folder = "./output/"

for manuscript in os.listdir(input_folder):
    print("\n \n \n MAPPING DOCUMENT: {} \n \n \n".format(manuscript))
    mapping_functions.map_response(schema, os.path.join(input_folder,manuscript), os.path.join(output_folder, manuscript + '.elastic.json'))


