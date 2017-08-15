
# coding: utf-8

# In[83]:

#es.get(index='trees_of_the_northeastern_united_states', doc_type='tree',id='5')


# In[13]:

#test search searching for NJ. Returns ranked results based on scores.
#res = es.search(index='trees_of_the_northeastern_united_states', doc_type='tree',body={'query':{'match':{'text':""}}})
#print res

#for result in res:
#print res['hits']['hits'][0]['_source']['text']
#print ""


# In[70]:

#indices exist
#for index in es.indices.get('*'):
#    print index


# In[9]:

#es.indices.delete('*')


# In[10]:

import elasticsearch
import os
import json
from flask import *
import math
from math import ceil

es = elasticsearch.Elasticsearch()
es.indices.delete("*")

mapping = {
  "settings": {
      "index" : {
        "analysis": {
            "analyzer":    {
              "tree_analyzer": {
                "type": "custom",
                "stopwords": "_english_",
                "tokenizer": "standard",
                "filter": ["lowercase","tree_synonyms"]
              }
            },
            "filter":{
              "tree_synonyms": {
                "type":   "synonym",
                "ignore_case": "true",
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
                  "summerwood, latewood",
                  "sourwood, abcdef1234"
                ]
              }
            }
          }
        }
    },
    "mappings" : {
      'tree': {
           "properties": {
                "title": {
                  "type": "string"
                },
                "text": {
                  "type": "string",
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
for base, subdirs, files in os.walk('Trees_Of_The_World'):
    for name in files:
        if ".json" in os.path.join(base,name):
            with open(os.path.join(base,name), 'r') as fp:
                data = json.load(fp)
            if not es.indices.exists(index=os.path.splitext(name)[0].lower()):
                es.indices.create(index=os.path.splitext(name)[0].lower(), body=mapping)
                for docs in data:
                    es.index(index=os.path.splitext(name)[0].lower(),doc_type='tree',id=docs,body=data[docs])
            #print es.indices.get_mapping(index=os.path.splitext(name)[0].lower(), doc_type='tree')


# in[ ]:
#res = es.search(index='trees_of_the_northeastern_united_states',doc_type='tree',body={'query':{'match':{'text':""}}})


# flask

# search function takes in a dict of keywords/values, and returns a list of results
def elasticsearch_search(query):
    res_list = []
    #    if query is dict:
    query['pinnate'] = query['leaves']=="pinnate"
    query['palmate'] = query['leaves']=="palmate"
    query['leaves_otherwise'] = query['leaves']=="leaves_otherwise"
#    for key, value in query.iteritems():
    print query
    res = es.search(index='trees_of_the_northeastern_united_states',
                    doc_type='tree',
                    body={'query':{'bool':{'should': [
                                             #{"match": {"title": query['title']}},
                                            {"match": {"text": query['keywords']}},
                                            {"match": {"compound": query['compound']}},
                                            {"match": {"coniferous": query['coniferous']}},
                                            {"match": {"opposite": query['opposite']}},
                                            {"match": {"leaves_otherwise": query['leaves_otherwise']}},
                                            {"match": {"pinnate": query['pinnate']}},
                                            {"match": {"palmate": query['palmate']}}
                                            ]}}})

    for each in res['hits']['hits']:
        print each['_source']['title']
        res_list.append(each['_source']['title'])
    return res_list

def find_article(tree):
    article = {}
    for base, subdirs, files in os.walk('Trees_Of_The_World'):
        for name in files:
            if ".json" in os.path.join(base,name):
                with open(os.path.join(base,name), 'r') as fp:
                    tree_data = json.load(fp)
                    for key in tree_data.keys():
                        if tree_data[key]['title'] == tree:
                            article = tree_data[key]
                            break
    return article



app = Flask(__name__)

class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

@app.route("/")
def search():
    return render_template('search_page.html')

PER_PAGE = 10
@app.route("/results", defaults={'page': 1})
@app.route("/results/page/<int:page>")
def results(page):
    try:
        query = {'keywords': request.args['keywords'],
                'compound': request.args['compound'],
                'coniferous': request.args['coniferous'],
                'opposite': request.args['opposite'],
                'leaves': request.args['leaves']}
        search_results = elasticsearch_search(query)
        results_on_page = split_result(page, PER_PAGE, search_results)
        pagination =  Pagination(page, 10, len(search_results))
        return render_template('result_page.html', pagination=pagination, results=results_on_page)
    except KeyError:
        return "Problem"

def split_result(page, PER_PAGE, results):
    start = (page-1)*PER_PAGE
    end = min(page*PER_PAGE, len(results))
    return results[start:end]

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    query = request.args['query']
    return url_for(request.endpoint, query=query, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.route("/article/tree")
def article():
    try:
        a = find_article(request.args['tree'])
        #a = "the tree..."
        return render_template('target_article.html', article=a)
    except KeyError:
        return "Problem"


if __name__ == "__main__":
    app.run()
