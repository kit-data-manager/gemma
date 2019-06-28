import requests, json, os, sys
from elasticsearch import Elasticsearch
import pprint

directory = sys.argv[1]
#directory = "./output/"

doc_ext = ".json"

res = requests.get('http://localhost:9200')
pprint.pprint(res.content)
es = Elasticsearch([{'host':'localhost', 'port':'9200'}])


def index_all(directory, doc_ext):
    i = 1
    for filename in os.listdir(directory):
        if filename.endswith(doc_ext):
            print("Reading file {}".format(filename))
            f = open(os.path.join(directory,filename), encoding="utf-8")
            content = f.read()
            es.index(index='textindex', ignore=400, doc_type='docket',id=i, body=json.loads(content))
            i += 1

def search_query(query, index, text):
    res = es.search(index="textindex",
                    body={"query": {query: {index: text}}})
    return res

index_all(directory, doc_ext)

# Example of query

res = search_query("match_phrase", "source.repository", "Bibliothèque Nationale de France")
print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
    pprint.pprint(hit["_source"])
print("Got %d Hits" % res['hits']['total']['value'])
