# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

import datetime
import functools
import json
import os
import os.path
import urlparse

from flask import request, session, render_template, redirect, url_for, jsonify, Response
import psycopg2

from csp.frontend.persona import verify_assertion
from csp.frontend import app
from csp.frontend.mozillians import lookup_mozillian
from csp.frontend.queries import *

#

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is None:
            session["next"] = request.url
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

#

def find_all_sites():
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(ALL_SITES_QUERY)
            return [{"id":row[0], "hostname":row[1]} for row in cursor]

def find_default_site(session):
    site = session.get("site")
    if site is None:
        with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
            with connection.cursor() as cursor:
                cursor.execute(FIND_FIRST_SITE_QUERY)
                row = cursor.fetchone()
                return row[0]

# directive, id, count
def find_top_violations(hostname):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_VIOLATIONS_QUERY, [hostname])
            return [row for row in cursor]

def find_top_pages(hostname):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_PAGES_QUERY, [hostname])
            return [row for row in cursor]

def find_top_documents_for_directive(hostname, directive_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_DOCUMENTS_FOR_DIRECTIVE_QUERY, [hostname, directive_id])
            return [row for row in cursor]

def find_document(document_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute("select id, value from documenturi where id=%s", [document_id])
            row = cursor.fetchone()
            return {"id":row[0], "uri":row[1]}

def find_directive(directive_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute("select id, value from violateddirective where id=%s", [directive_id])
            row = cursor.fetchone()
            return {"id":row[0], "created": 0, "directive":row[1]}

def find_top_violations_for_document(document_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_VIOLATIONS_FOR_DOCUMENT_QUERY, [document_id])
            return [row for row in cursor]

def find_top_blockers_for_site(hostname):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_BLOCKERS_FOR_SITE_QUERY, [hostname])
            return [row for row in cursor]

def find_top_blockers_for_document(document_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TOP_BLOCKERS_FOR_DOCUMENT_QUERY, [document_id])
            return [row for row in cursor]

def find_useragents_for_site(hostname):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(USERAGENTS_FOR_SITE_QUERY, [hostname])
            return [row for row in cursor]

def find_useragents_for_directive(hostname, directive_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(USERAGENTS_FOR_DIRECTIVE_QUERY, [hostname, directive_id])
            return [row for row in cursor]

#

def _fetch_rows(cursor):
    for row in cursor:
        cols = [d[0] for d in cursor.description]
        yield dict(zip(cols, row))

def generate_raw_reports_for_document(hostname, directive_id, document_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(FULL_REPORTS_FOR_SITE_DIRECTIVE_DOCUMENT_QUERY, [hostname, directive_id, document_id])
            return [json.dumps(row, indent=3) for row in _fetch_rows(cursor)]

#

@app.route("/")
def index():
    if session.get("email") is None:
        return redirect(url_for("login"))
    return redirect(url_for("site", hostname="stefan.arentz.ca"))
    #return redirect(url_for("site", hostname=find_default_site(session)))

@app.route("/login")
def login():
    if session.get("email") is not None:
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/heartbeat")
def heartbeat():
    return "OK"

#

@app.route("/persona/login", methods=["POST"])
def persona_login():
    receipt = verify_assertion(request.form["assertion"], request.host)
    if not receipt:
        return jsonify(success=False)
    email = receipt["email"]
    if not email.endswith("@mozilla.com") and not email.endswith("@mozillafoundation.org"):
        mozillian = lookup_mozillian(app.config["MOZILLIANS_APP_NAME"],
                                     app.config["MOZILLIANS_APP_KEY"], email)
        if not mozillian or not mozillian["is_vouched"]:
            return jsonify(success=False, error="only-mozilla")
    session["email"] = receipt["email"]
    return jsonify(success=True, email=receipt["email"], next=session.get("next"))

#

@app.route("/site/<hostname>")
@login_required
def site(hostname=None):
    return render_template("site.html",
                           hostname=hostname,
                           sites=find_all_sites(),
                           top_violations=find_top_violations(hostname),
                           top_pages=find_top_pages(hostname),
                           top_blockers=find_top_blockers_for_site(hostname),
                           top_useragents=find_useragents_for_site(hostname))

@app.route("/site/<hostname>/directive/<directive_id>")
@login_required
def site_directive(hostname, directive_id):
    return render_template("directive.html",
                           hostname=hostname,
                           sites=find_all_sites(),
                           directive=find_directive(directive_id),
                           top_documents=find_top_documents_for_directive(hostname, directive_id),
                           top_useragents=find_useragents_for_directive(hostname, directive_id))

@app.route("/site/<hostname>/directive/<directive_id>/document/<document_id>")
@login_required
def site_directive_document(hostname, directive_id, document_id):
    return render_template("site-directive-document.html",
                           sites=find_all_sites(),
                           directive=find_directive(directive_id),
                           document=find_document(document_id),
                           reports=generate_raw_reports_for_document(hostname, directive_id, document_id),
                           hostname=hostname)
#

@app.route("/site/<hostname>/document/<document_id>")
@login_required
def site_document(hostname, document_id):
    return render_template("document.html",
                           sites=find_all_sites(),
                           hostname=hostname,
                           document=find_document(document_id),
                           top_violations=find_top_violations_for_document(document_id),
                           top_blockers=find_top_blockers_for_document(document_id))

# Chart data

@app.route("/data/timeline/site/<hostname>/directive/<directive_id>")
@login_required
def data_measure_violations_all(hostname, directive_id):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TIMELINE_VIOLATIONS_FOR_DIRECTIVE_QUERY, [hostname, directive_id])
            data = [{"x": idx, "y": row[1]} for idx, row in enumerate(cursor.fetchall())]
            return jsonify(success=True, data=data)

@app.route("/data/timeline/site/<hostname>")
@login_required
def data_timeline_site(hostname):
    with psycopg2.connect("dbname=csp user=csp password=csp") as connection:
        with connection.cursor() as cursor:
            cursor.execute(TIMELINE_VIOLATIONS_FOR_HOST_QUERY, [hostname])
            data = [{"x": idx, "y": row[1]} for idx, row in enumerate(cursor.fetchall())]
            return jsonify(success=True, data=data)
