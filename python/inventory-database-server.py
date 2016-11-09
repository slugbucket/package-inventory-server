from flask import Flask, abort, request
import os.path

import dbconf
cnx = dbconf.dbconnect

app = Flask(__name__)
#
# Based on http://flask.pocoo.org/docs/0.11/quickstart/#routing
#
@app.route('/package-inventory/<hostname>/<pkgname>', methods=["GET"])
def get_inventory_package(hostname):
    fn = "cache/%s" % hostname
    if os.path.isfile(fn):
        fh = open(fn ,"r")
        return( fh.read() )
    else:
        abort(404)



# Method to check that the input data matches expectations
def validate_input(data):
    return 1

if __name__ == "__main__":
    app.run()
