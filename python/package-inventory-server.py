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

@app.route('/package-inventory/<hostname>/new', methods=["POST"])
def post_inventory_package(hostname):
    if not validate_input(request.data):
        abort(400)

    fn = "cache/%s" % hostname
    fh = open(fn ,"w")
    print( "Writing submission to %s" % fn )
    if fh.write( str( request.data ) ):
        st = "{\"status\":\"Received 3 packages for %s.\"}" % hostname
        return ( st )
    else:
        abort(400)

# Method to check that the input data matches expectations
def validate_input(data):
    return 1

if __name__ == "__main__":
    app.run()
