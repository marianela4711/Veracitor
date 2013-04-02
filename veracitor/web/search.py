from flask import Flask, render_template, request, redirect, url_for
from ..database import *

import json

from veracitor.web import app

from veracitor.crawler import crawlInterface as ci

# crawler variables
crawl_id_counter = 0
crawl_ids = {}

ci.set_callback(crawl_callback)

"""
Callback function for the crawler
"""
def crawl_callback(item, id):
    crawl_ids[id] = item

"""
Returns a unique crawl procedure  id.
"""
def get_unique_crawl_id():
    id = '#' + crawl_id_counter
    crawl_id_counter += 1
    return id

"""
Starts a crawler to crawl the given URL for an entity.

"""
@app.route('/start_crawl_procedure', methods=['GET','POST'])
def start_crawl_procedure():
    if request.method == 'POST':
        procedure = {}
        error = {
            'message' : 'none',
            'type' : 'none'
        }

        if request.form:
            f = request.form

            if not f['url']:
                error = {
                    'message': 'No URL specified.',
                    'type': 'no_url'
                }

            if error['type'] == 'none':
                id = get_unique_crawl_id()

                crawl_ids[id] = None

                # start scraping the specified URL
                ci.scrape_article(f['url'], id)

                procedure = {
                    'message': 'Started crawling %s.' % f['url'],
                    'callback_url': '/check_crawl_procedure',
                    'id': id
                }
        else:
            error = {
                'message': 'Form data error.',
                'type': 'form_error'
            }

        return json.dumps({ 'error': error, 'procedure': procedure })

    return redirect(url_for('index'))

"""
Handles the connection between the client and its currently
running SUNNY procedures.

"""
@app.route('/check_crawl_procedure', methods=['GET','POST'])
def check_crawl_procedure():

    if request.method == 'POST':
        procedure = {}
        error = {
            'message' : 'none',
            'type' : 'none'
        }

        if request.form:
            f = request.form

            if not f['id']:
                error = {
                    'message': 'No id specified.',
                    'type': 'no_source'
                }

            if error['type'] == 'none':
                if crawl_ids[f['id']]:
                    procedure = {
                        'status': 'done',
                        'id': f['id']
                        #'item': crawl_ids[f['id']]
                    }
                    # remove the procedure
                    del crawl_ids[f['id']]
                else:
                    procedure = {
                        'status': 'processing'
                    }

        else:
            error = {
                'message': 'Form data error.',
                'type': 'form_error'
            }

        return json.dumps({ 'error': error, 'procedure': procedure })

    return redirect(url_for('index'))

"""
Performs a search in the database for producers that match the given
parameters. The client is returned a JSON object with information
about possible errors and computed HTML code representing the result
from the performed search.
"""
@app.route('/search_producers', methods=['GET','POST'])
def search_producers():

    if request.method == 'POST':
        error = {
            'message' : 'none',
            'type' : 'none'
        }
        html = ''

        if request.form:
            f = request.form

            data = {}

            if not f['name']:
                error = {
                    'message' : 'No search parameter.',
                    'type' : 'no_param'
                }
            elif not f['type']:
                error = {
                    'message' : 'No type chosen.',
                    'type' : 'no_type'
                }

            if error['type'] == 'none':
                res = extractor.search_producers(possible_prod=f['name'],
                                                 type_of=f['type'])

                if res:
                    data = { 'result' : res }
                else:
                    error = {
                        'message' : 'Could not find anything.',
                        'type' : 'no_result'
                    }

            if not error['type'] == 'none':
                data = { 'error' : error }

            html = render_template('tabs/search_results.html', data=data)
        else:
            error = {
                'message' : 'Form data error.',
                'type' : 'form_error'
            }

        return json.dumps({ 'error' : error, 'html' : html })

    return redirect(url_for('index'))

"""
Initializes the web page.
"""
@app.route('/')
def index():
    veracitor = {
        'title' : 'Veracitor',
        'tabs' : [
            {
                'name' : 'Search',
                'key' : 'search',
                'viewid' : 'search_view',
                'menuid' : 'search_menu',
                'url' : 'tabs/search_tab.html'
            },
            {
                'name' : 'Network',
                'key' : 'network',
                'viewid' : 'network_view',
                'menuid' : 'network_menu',
                'url' : 'tabs/network_tab.html'
            },
            {
                'name' : 'Ratings',
                'key' : 'ratings',
                'viewid' : 'ratings_view',
                'menuid' : 'ratings_menu',
                'url' : 'tabs/ratings_tab.html'
            },
            {
                'name' : 'Account',
                'key' : 'account',
                'viewid' : 'account_view',
                'menuid' : 'account_menu',
                'url' : 'tabs/account_tab.html'
            }
        ]
    }
    return render_template('index.html', vera=veracitor)
