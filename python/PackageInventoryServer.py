#!/usr/bin/env python
#
# Run the server with 
# $ export FLASK_APP=PackageInventoryServer.py 
# $ flask run --host=0.0.0.0
#
from flask import Flask, abort, request
import os.path

app = Flask(__name__)
#
# Based on http://flask.pocoo.org/docs/0.11/quickstart/#routing
#
@app.route('/package-inventory/<hostname>', methods=["GET"])
def get_inventory_package(hostname):
    fn = "cache/%s" % hostname
    if os.path.isfile(fn):
        fh = open(fn ,"r")
        return( fh.read() )
    else:
        abort(404)

@app.route('/package-inventory/packages/new', methods=["POST"])
def post_inventory_package():
    if validate_input(request) == False:
        abort(400)
    jdata = request.get_json()

    if (jdata['hostname'] != None):
        hostname = jdata['hostname']
    else:
        hostname = request.host
    fn = "cache/%s" % hostname
    fh = open(fn ,"w")
    if fh.write( str(request.data, 'utf-8') ):
        st = "{\"status\":\"Received packages for %s.\"}" % hostname
        return ( st )
    else:
        abort(400)

# Method to check that the input data matches expectations
def validate_input(request):
    if( request.is_json == False ):
        return False

    return 1

if __name__ == "__main__":
    app.run()
