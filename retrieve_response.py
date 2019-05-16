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

output_folder = sys.argv[1]

payload = "{\n \t\"resourceType\": {\n \t\t\"typeGeneral\":\"TEXT\"\n \t}\n}"
headers = {'Content-Type': "application/json", 'cache-control': "no-cache"}

size = 20
page = 0



def http_call(TYPE, host=HOST, port=PORT, endpoint='', search='', query='', payload='', headers={}):
    check_http_method(TYPE)
    conn = http.client.HTTPConnection(host, port)
    if search != '' or query != '':
        endpoint = os.path.join(endpoint, search + query)
    url = os.path.join(URL, endpoint)
    print('URL: ', url)
    conn.request(TYPE, url, payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    return data


def check_http_method(method):
    assert(isinstance(method, str)), 'method must be a string'
    list = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE']
    if method not in list:
        print("{} not allowed. Use: 'POST', 'GET', 'PUT', 'PATCH', 'DELETE'".format(method))
        return


def download_file(file_id, extention='xml'):
    endpoint = 'data/manuscript_metadata.' + extention
    url = os.path.join(URL, file_id, endpoint)
    output_file = file_id + "." + extention
    wget.download(url, os.path.join(output_folder, output_file))



while True:
    retrieve = 'search?size=' + str(size) + '&page=' + str(page)
    data = http_call('POST', search=retrieve, payload=payload, headers=headers)
    print('{} results at page {}'.format(len(data), page))
    if len(data) == 0:
        break

    for resourse in data:
        manuscript_id = resourse['id']
        print("manuscript id: {}".format(manuscript_id))
        if resourse['state'] == "REVOKED":
            print("Status of resource {} is {}".format(resourse, resourse['state']))
            continue
        assert(resourse['resourceType']['value'] == 'manuscriptMetadata'), "resourceType is not manuscriptMetadata"
        download_file(manuscript_id)

    if len(data) == size:
        page += 1
    else:
        break
