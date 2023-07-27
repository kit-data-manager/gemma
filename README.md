# Gemma

Gemma is a Generic Metadata Mapper written in Python. It allows to map metadata in JSON or XML format into another representation, e.g. for indexing at Elastic, using a custom mapping description.

## Manuscript metadata mapping

Useful files:
- `./sample/schema-for-xml-response.json` contains the schema to map the xml response. The mapping has been done according to the TEI, suggested by Germaine;
- `mapping_functions.py` contains the functions needed to run the mapping of the metadata, in order to create a JSON document ready to be indexed by elasticSearch.

## Ubuntu installation and settings
	apt-get update
	apt-get install python3 python3-pip
	pip3 install xmltodict wget
	export PYTHONIOENCODING=UTF-8

## MacOS installation and settings
If not present, install Homebrew:

	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	
Then, install Python 3:

	brew install python3
	
Check whether Homebrew have already installed `pip` pointing to the Homebrew’d Python 3 for you:

	which pip
	which pip3
	
If your `pip` already points to Python3:

	pip install xmltodict wget
	
Otherwise:

	pip3 install xmltodict wget

## Explanation and instructions
There are two codes: one to download all the manuscript metadata (i.e. the responses) from the episteme repo, the other to map the metadata according to the schema.
Both are partially interactive, so the input and output folders must be inserted by the user.

### Download the manuscript metadata
The code retrieves all the manuscript resources in the episteme repo, and downloads the XML response naming it locally as its id.
The http connection is hardcoded, while the local folder (which must already exist) where to download the files must be insterted by the user.
To run the code:

	python3 retrieve_response.py $local_folder

### Create the JSON file for elasticSearch
The code creates a JSON file for each manuscript, extracting the relevant metadata (suggested by Germaine) from the XML response file.
These metadata can be then indexed in elasticSearch.
The mapping is done following a schema, provided by the `./sample/schema-for-xml-response.json` file.
The mapping cannot be granular for some entries, due to a couple of reasons:
1. In some files, the content is in the expected key, while in some others it is in a more nested key. For example, it could be in `source.settlement` or in `source.settlement.rd.#text`. This applies to:
	- `source.settlement`
	- `content.locus`
2. In some files, the value is a list, which is more complicated to manage. This will be done in the second version. Up to now, all the list (with its nested dictionaries, which can in future be indexed) is just casted as a string. This applies to:
	- `dimensions`
	- `hand note`
	- `provenance event`
	- `listBibl.bibl`

To run the code:

	python3 mapping.py $schema $input_folder $output_folder

where `$schema` is the schema file, in this case `./sample/schema-for-xml-response.json`, `$input_folder` is the folder where the XML responses are, `$output_folder` is the folder (which must already exist) where the JSON files will be created.
The output JSON files are named as the XML file + the extension `.elastic.json`, so for example `manuscript_id.xml.elastic.json`.

## To be fixed in version 2:
- manage nested dictionaries within lists
- manage mandatory fields (the ones in the basic minimal schema)
- manage entries which have `None` in the XML response in a different way from missing entries
- go beyond full-text search, starting e.g. from dates and dimensions

# Elasticsearch

To download, install and run an Elasticsearch instance, follow the instructions of the web page: https://www.elastic.co/downloads/elasticsearch

## Indexing

The code `elastic_indexing.py` allows to index all the manuscripts JSON files (by default) in a given folder, which must be provided.
Addotional packages are needed:

	pip3 install requests, elasticsearch

To run it:

	python3 elastic_indexing.py JSON_directory

## Search using the Python code

The code `elastic_indexing.py` already contains a function using the python elasticsearch client and an example of search. 
An other option is to use Kibana. 

## Seach using Kibana

To download, install and run Kibana on top of your Elasticsearch instance, follow the instructions on the web page: https://www.elastic.co/downloads/kibana 

To search all manuscripts, write on Kibana dashboard:

	GET episteme/_search
	{
  	  "query": {
    	    "match_all": { }
	  }
	}

In the response, `hits.value` is the number of found hits: 

	"hits" : {
	  "total" : {
	  "value" : 81,
	  "relation" : "eq"
	}

To search by exact match of a word, write on Kibana dashboard:

	GET episteme/_search
	{
	  "query": {
	    "match": {
	      "index.name.with.dots.if.nested": "word to match"
	    }
	  }
	}

To search by exact match of a sentence, write on Kibana dashboard:

        GET episteme/_search
        {
          "query": {
            "match_phrase": {
              "index.name.with.dots.if.nested": "sentence to match"
            }
          }
        }

To select the index name, please consult the JSON schema `schema-for-xml-response.json`.
It works also with Greek, special French, and German letters. 

