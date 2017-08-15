import elasticsearch
import os
import json
from flask import *
import math
from math import ceil

es = elasticsearch.Elasticsearch()
mapping = {
  "settings": {
      "analysis": {
        "filter":{
          "tree_synonyms": {
            "type": "synonym",
            "synonyms": [
              "trunk, log, stem, bole",
              "wood, heartwood",
              "bark, outer-bark, outer bark, inner-bark, inner bark",
              "phloem, inner-bark, inner bark",
              "xylem, sapwood",
              "crown, canopy",
              "dendrology, tree identification, tree study",
              "earlywood, early-wood, springwood, spring-wood",
              "foliage, leaves",
              "forb, herb",
              "resin, sap",
              "summerwood, latewood"
            ]
          }
        },
        "analyzer":    {
          "tree_analyzer": {
            "type": "custom",
            "stopwords": "_english_",
            "char_filter": "icu_normalizer",
            "tokenizer": "standard",
            "filter": ["lowercase", "tree_synonyms"]
          }
        }
      }
    },
    "mappings" : {
      "tree": {
           "properties": {
                "title": {
                  "type": "string"
                },
                "description": {
                    "type": "text",
                    "analyzer": "tree_analyzer"
                },
                "compound": {
                    "type": "boolean"
                },
                "coniferous": {
                    "type": "boolean"
                },
                "opposite": {
                    "type": "boolean"
                },
                "leaves_otherwise": {
                    "type": "boolean"
                },
                "pinnate": {
                    "type": "boolean"
                },
                "palmate": {
                    "type": "boolean"
                }

            }
        }
    }
}

#Test. To get working basic example, run with body = data[docs]
for base, subdirs, files in os.walk('/Users/jiaqi/Documents/Brandeis/COSI 132a Information Retrieval/Project/Trees_Of_The_World'):
    for name in files:
        if ".json" in os.path.join(base,name):
            with open(os.path.join(base,name), 'r') as fp:
                data = json.load(fp)
                es.index(index=os.path.splitext(name)[0].lower(),doc_type='tree', body=mapping)
                #print es.indices.get_mapping(os.path.splitext(name)[0].lower())
            for docs in data:
                es.index(index=os.path.splitext(name)[0].lower(),doc_type='tree',id=docs,body=data[docs])


query = {'keywords': u'tree', 'compound': u'false', 'leaves': u'leaves_otherwise'}
#if query is dict:
query['pinnate'] = query['leaves']=="pinnate"
query['palmate'] = query['leaves']=="palmate"
query['leaves_otherwise'] = query['leaves']=="leaves_otherwise"

print query

res = es.search(index='trees_of_the_northeastern_united_states',
                    doc_type='tree',
                    body={'size': 100, 'query':{"multi_match": {"query": query['keywords'],
                                    "fields": ["title", "text"]}}})
#for each in res['hits']['hits']:
    #print each['_source']['title']
res_list=[]

for each in res['hits']['hits']:
    print each['_source']['title']
    res_list.append(each)
    print '\n'


es.indices.delete('*')
