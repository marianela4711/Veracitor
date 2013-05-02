# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, jsonify

import json

from veracitor.web import app
from veracitor.web.utils import store_job_result
from veracitor.database import user, group, information, extractor

import veracitor.tasks.ratings as ratings

@app.route('/jobs/ratings/user', methods=['GET', 'POST'])
def get_user():
    """Gets the specified user from the database.

    URL Structure:
        /jobs/ratings/user

    Method:
        POST

    Parameters:
        name (str): The name of the user.

    Returns:
        Upon success, returns the user as a json object.

    Errors:
        400 - Bad syntax/No name/type in request
        405 - Method not allowed

    """
    if not request.method == 'POST':
        return "nope"
        abort(405)
    try:
        user_id = request.form['user_id']
        userObj = extractor.get_user(user_id)
    except NotInDatabase:
        return "not in databaseteafw"
    except:
        return "bajs"
        abort(400)

    return "snopp"
    


@app.route('/jobs/ratings/rate_producer', methods=['GET', 'POST'])
def rate_producer():
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(request.form['username']) # TODO: Use real session user
        user.rate_source(request.form['producer'], request.form['tag'], int(request.form['rating']))
        #user.save()
    except:
        abort(400)

    # TODO: Render json

@app.route('/jobs/ratings/rate_information', methods=['GET', 'POST'])
def rate_information():
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(request.form['username']) # TODO: Use real session user
        user.rate_information(request.form['information'], int(request.form['rating']))
        #user.save()
    except:
        abort(400)

    # TODO: Render json

@app.route('/jobs/ratings/create_group', methods=['GET', 'POST'])
def create_group():
    """
    Creates a group with the specified name.

    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(request.form['username']) # TODO: Use real session user
        user.create_group(request.form['name'])
        #user.save()
    except:
        abort(400)

    # TODO: Render json

@app.route('/jobs/ratings/rate_group', methods=['GET', 'POST'])
def rate_group():
    """
    Rate a group.

    """
    if not request.method == 'POST':
        abort(405)
    try:
        user = extractor.get_user(request.form['username']) # TODO: Use real session user
        user.rate_group(request.form['name'], request.form['tag'],
                        int(request.form['rating']))
        #user.save()
    except:
        abort(400)

    # TODO: Render json
    
