from flask import *
#import os.path
import math
from math import ceil
#import heapq
#import operator

#key words & boolean values

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
        query = request.args['keywords']
        #search_results = vs_search(str(query))
        search_results = request.args['keywords']
        #search_results = [[request.args['keywords'],
        #                request.args['compound'],
        #                request.args['coniferous'],
        #                request.args['opposite'],
        #                request.args['leaves']]]
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


@app.route("/article/title")
def article():
    try:
        #a = find_article(request.args['title'])
        a = "the tree..."
        return render_template('target_article.html', article=a)
    except KeyError:
        return "Problem"


if __name__ == "__main__":
    app.run()
