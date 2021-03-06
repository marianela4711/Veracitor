
# -*- coding: utf-8 -*-

# ratings.py
# ========

"""
.. module:: ratings
      :synopsis: Defines server logic for the ratings tab

REST API implementation for server requests concerning the ratings tab.
   
This applies to all functions:
   
URL Structure:
   `jobs/ratings/<MODULE NAME>`

Errors:
   - **400** - Bad syntax
   - **405** - Method not allowed

.. note::
   Though the URL structure begins with `jobs/`, these methods do not start
   any Celery tasks or jobs.


Functions
---------
   

.. moduleauthor:: Martin Runelov <mrunelov@kth.se
.. moduleauthor:: Daniel Molin <dmol@kth.se>

"""

from flask import Flask, render_template, session, request, redirect, url_for, jsonify, abort

from veracitor.web import app, utils
from veracitor.web.utils import store_job_result, get_user_as_dict
from veracitor.database import user, group, information, extractor

import veracitor.tasks.ratings as ratings

log = app.logger.debug


@app.route('/jobs/ratings/render', methods=['GET', 'POST'])
def render_ratings():
    """
    Fetches the current user and renders the Ratings tab

    Method:
        POST
    
    Returns:
        *html* (str): The html used to render the Ratings tab

        *producers* (dict): A dictionary of the producers that the currently logged in user has rated

        *information* (dict): A dictionary of the information that the currently logged in user has rated
    
    """
    if not request.method == 'POST':
        abort(405)
    try:
        renderDict = {}
        renderDict = utils.get_user_as_dict(session['user_name'])
        renderDict['prodtags'] = get_used_prod_tags()
        renderDict['infotags'] = get_used_info_tags()
        renderDict['tags'] = get_all_tags()
        producers = renderDict['source_ratings']
        information = renderDict['info_ratings']
        html = render_template('tabs/ratings_tab_content.html', renderDict=renderDict)

    except Exception, e:
        log(e)
        abort(400)

    return jsonify(html=html, producers=producers, information=information)

@app.route('/jobs/ratings/rate_producer', methods=['GET', 'POST'])
def rate_producer():
    """
    Rates a producer

    Method:
        POST

    Parameters:
        *producer* (str): The producer to be rated

        *tag* (str): The tag with which to rate

        *rating* (str): The rating with which to rate

    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(session['user_name'])
        user.rate_source(request.form['producer'],
                         request.form['tag'], int(request.form['rating']))
    except:
        abort(400)

    # TODO: Render json

@app.route('/jobs/ratings/rate_information', methods=['GET', 'POST'])
def rate_information():
    """
    Rates information

    Method:
        POST

    Parameters:
        *information* (str): The information to be rated

        *rating* (str): The rating with which to rate
   
    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(session['user_name'])
        user.rate_information(request.form['information'],
                              int(request.form['rating']))
    except:
        abort(400)

    # TODO: Render json

@app.route('/jobs/ratings/create_group', methods=['GET', 'POST'])
def create_group():
    """
    Creates a group with the specified name.

    Method:
        POST

    Parameters:
        *name* (str): The name of the group that will be created
        *tag* (str): The tag to associate with the group

    Returns:
        The name of the created group.
        
    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(session['user_name'])
        user.create_group(request.form['name'], request.form['tag'])

        return request.form['name']
    except Exception, e:
        log(e)        
        abort(400)
        return "Fail"

    # TODO: Render json

@app.route('/jobs/ratings/rate_group', methods=['GET', 'POST'])
def rate_group():
    """
    Rates a group

    Method:
        POST

    Parameters:
        *name* (str): The name of the group to be rated

        *rating* (str): The rating with which to rate

    Returns:
        A status string (currently without purpose)

    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(session['user_name'])
        user.rate_group(str(request.form['name']), int(request.form['rating']))
        user.save()
    
        return request.form['rating']
    except Exception, e:
        log(e)
        return "Fail"
        abort(400)

    # TODO: Render json


def get_used_prod_tags():
    """
    Get a list of all tags that the user has rated producers with.
    
    Method:
       POST

    Returns:
       A dict containing the used tags::

          {
             "tags" : tags_used ([(str), ]), 
          }

    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(session['user_name'])

        tags_used = [] 
        for sr in user.source_ratings:
            tags_used.extend(user.source_ratings[sr].keys())
            
        return list(set(tags_used))
    except:
        abort(400)


def get_used_info_tags():
    """
    Get a list of all tags that the user has rated information with.

    Method:
       POST

    Returns:
       A dict containing the used tags::

          {
             "tags" : tags_used ([(str), ]), 
          }

    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(session['user_name'])
        tags_used = []
        for info_rating in user.info_ratings.keys():
            tags_used.extend([tag.name for tag in extractor.get_information(__safe_string(info_rating)).tags])

        return list(set(tags_used))
    except Exception, e:
        log(e)
        abort(400)


def get_all_tags():
    try:
        tag_names = [tag.name for tag in extractor.get_all_tags()]
        return tag_names
    except:
        abort(400)

    
def __safe_string(url):
    """
    Help method to change url representation.
    TODO: Remove any need for this beyond private methods in the database module
    
    """
    return url.replace("|", ".")
