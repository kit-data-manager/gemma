import http.client
import os
import json
import wget
import mapping_functions
import pprint
import sys

HOST = 'episteme2.scc.kit.edu'
PORT = '8080'
URL = os.path.join('http://' + HOST + ':' + PORT, 'api/v1/dataresources')

payload = "{\n \t\"resourceType\": {\n \t\t\"typeGeneral\":\"TEXT\"\n \t}\n}"
headers = {'Content-Type': "application/json", 'cache-control': "no-cache"}

size = 20
page = 0

schema = sys.argv[1]
input_folder = sys.argv[2]
output_folder = sys.argv[3]


for manuscript in os.listdir(input_folder):
    print("\n \n \n MAPPING DOCUMENT: {} \n \n \n".format(manuscript))
    mapping_functions.map_response(schema, os.path.join(input_folder,manuscript), os.path.join(output_folder, manuscript + '.elastic.json'))


