#!/usr/bin/env python
#
# Run the server with
# $ export FLASK_APP=PackageInventoryServer.py
# $ flask run --host=0.0.0.0
#
from flask import Flask, abort, request, Response
import os.path
import subprocess
import OpenSSL
import json

app = Flask(__name__)

# Method to check whether a client submitted cert for the requesting hostname
# matches the local certificate store. If yes, proceed. If not, return 400
# params:
#  hostnme: string: identifies the fully qualified name of the cert to retrieve
# returns
#   Boolean:
def validate_client_cert():
    pass

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

@app.route('/package-inventory/client-cert/new', methods=["POST"])
def get_client_csr():
    client = "fnunbob.localdomain"
    certdir = "/home/julian/Projects/python/client-cert-auth"
    resp = Response(response = "", status = 200, content_type = "application/json")
    #response.content_type = "application/json"
    #response.status = 200
    rc = sign_csr(certdir, client, request.data)

    if rc == False:
        resp.status   = 400
        resp.response = "{'ERROR': 'cert sign request failed.'}"
    else:
        outcert  = certdir + "/signed-certs/" + client + ".cert.pem"
        if os.path.isfile(outcert):
            jdata = {}
            fh = open(outcert ,"r")
            jdata['signature'] = fh.read()
            print("get_client_csr: Sending signed cert to client: %s." % outcert)
            #resp.status = ("{'signature': '%s'}" % cc)
            resp.status = json.JSONEncoder().encode( jdata )
        else:
            resp.status_code   = 400
            resp.status = ("{'ERROR': 'Signed cert cannot be found for %s.'}" % client)
    #print("get_client_csr: Sending response: " % str(resp.status))
    return(resp)

def sign_csr(certdir, client, csr):
    """
    Method to sign a csr
    Params:
     certdir: String: identifies the directory where the intermedite signing
                      certificate is to be found
     jdata: JSON: object containing the client name and CSR data
    Returns:
     String: certificate to send back to client
    """
    print("sign_csr: Signing csr for %s." % client)
    #client = jdata['hostname']
    #csr = jdata['csr']

    # Save the CSR data to disk for processing
    csrconf  = certdir + "/intermediate-ca/intermediate-openssl.conf"
    csrdir   = certdir + "/" + "cert-requests"
    csrfile  = csrdir + "/" + client + ".csr.pem"
    passfile = certdir + "/intermediate-ca/passphrase"
    outcert  = certdir + "/signed-certs/" + client + ".cert.pem"

    # Show us what you've got
    print("sign_csr: openssl conf: %s" % csrconf)
    print("sign_csr: signed_cert: %s" % outcert)
    print("sign_csr: csr_file: %s" % csrfile)

    if os.path.isfile(outcert):
        print("sign_csr: certfile, %s, already exists." % outcert)
        abort(400)
    else:
        fh = open(csrfile ,"wb")
        fh.write( csr )
        fh.close()

    #sign_cert = ("openssl ca -config intermediate/openssl.cnf "
    #             "-extensions server_cert -days 375 -notext -md sha256 "
    #             "-in intermediate/csr/www.example.com.csr.pem         "
    #             "-out intermediate/certs/www.example.com.cert.pem     "
    #             % (csrfile, outcert) )
    sign_cert = ("openssl ca -config %s -in %s   "
                 "-passin file:%s -batch -out %s "
                 "-extensions server_cert "
                 "-days 375 -notext -md sha256 "
                 % (csrconf, csrfile, passfile, outcert) )
    print("sign_csr: create cert in %s with %s" % (outcert, sign_cert))
    output = subprocess.getoutput(sign_cert)
    return(output)

def validate_input(request):
    """
    Method to check that the input data matches expectations
    params:
     request: request data
    Returns:
      Boolean: true if submitted data is good, false otherwise
    """
    if( request.is_json == False ):
        return False

    return 1

if __name__ == "__main__":
    app.run()
