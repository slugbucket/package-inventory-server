#!/usr/bin/env python
#
# Run the server with
# $ export FLASK_APP=PackageInventoryServer.py
# $ flask run --host=0.0.0.0
#
from flask import Flask, abort, request, Response, redirect
import os
import subprocess
import OpenSSL
import json

app = Flask(__name__)

"""
Method to check whether a client submitted cert for the requesting hostname
matches the local certificate store. If yes, proceed. If not, return 400
params:
 hostnme: string: identifies the fully qualified name of the cert to retrieve
returns
  Boolean:
"""
def validate_client_cert():
    pass

@app.route('/package-inventory/heartbeat', methods=["GET"])
def heartbeat():
    return "OK"

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
"""
Route to accept a list of packages
params:
  JSON data identifying client and list of packages
returns:
  Response object indicating the status
"""
    resp = Response(response = "", status = 200, content_type = "application/json")
    print("post_inventory_package: Validating package data: %s" % request)
    if validate_input(request) == False:
        print("post_inventory_package: data validation failed. Exit with 400 status.")
        resp.status_code = 400
        jdata = [ "status", "Input validation failure."]
        resp.status = json.JSONEncoder().encode( jdata )
        return(resp)

    jdata = request.get_json()
    print("post_inventory_package: Received package data: %s" % jdata)
    if (jdata['hostname'] != None):
        hostname = jdata['hostname']
    else:
        hostname = request.host

    print("post_inventory_package: Saving package data for %s" % hostname)

    try:
        fn = "cache/%s" % hostname
        fh = open(fn ,"w")
        if fh.write( str(request.data, 'utf-8') ):
            resp.status = "{\"status\":\"Received packages for %s.\"}" % hostname
    except FileNotFoundError as fnfe:
        print("post_inventory_package: Cannot save cache file, %s: %s" % (fn, fnfe))
    else:
        resp.status_code = 404
        resp.status = "{\"status\":\"No packages cached for %s.\"}" % hostname

    return (resp)

@app.route('/package-inventory/client-cert/<certname>', methods=["GET"])
def get_client_cert(certname):
    """
    Method to retrieve a client certificate created after a CSR has been
    processed. The cert is deleted as part of this request.
    Params:
      <certname>: Taken from the request
    returns:
      string: pkcs10 content containing the cert; 404 error if the cert
              has already been downloaded or otherwise does not exist.
    """
    certdir = "/home/julian/Projects/client-cert-auth/intermediate-ca/newcerts/"
    certfile = certdir + certname
    print("get_client_cert: Received download request for %s." % certfile)
    resp = Response(response = "", status = 200, content_type = "text/plain")
    if(os.path.isfile(certfile) and os.path.getsize(certfile) > 0):
        fh = open(certfile ,"r")
        cert = fh.read()
        fh.close()
        print("get_client_cert: Sending signed cert from %s." % certfile)
        print("get_client_cert: Deleting server-side cert at %s" % certfile)
        os.unlink(certfile)
        return(cert)
    else:
        resp.status_code = 404

    return(resp)

@app.route('/package-inventory/client-cert/new', methods=["POST"])
def post_client_csr():
    """
    Method that receives a Certificate Signing Request (CSR) from a client.
    We take the submitted CSR and sign it and save the certificate and send
    back a 301 redirect to a cert download route
    params:
      None: only POSTed request data is used
    returns:
      Response: 301 redirect to /package-inventory/client-cert/<cert-name>
    """
    client = "fnunbob.localdomain"
    certdir = "/home/julian/Projects/client-cert-auth/intermediate-ca"
    resp = Response(response = "", status = 200, content_type = "application/json")
    rc = sign_csr(certdir, client, request.data)

    if rc == False:
        resp.status   = 400
        resp.response = "{'ERROR': 'cert sign request failed.'}"
    else:
        outcert  = certdir + "/newcerts/" + client + ".cert.pem"
        if os.path.isfile(outcert):
            return redirect("https://inventory-master.localdomain/package-inventory/client-cert/" + client + ".cert.pem", code=301)
        else:
            resp.status_code   = 404
            resp.status = ("{'ERROR': 'Signed cert cannot be found for %s.'}" % client)
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
    # Save the CSR data to disk for processing
    csrconf  = certdir + "/intermediate-openssl.conf"
    csrdir   = certdir + "/csr"
    csrfile  = csrdir  + "/" + client + ".csr.pem"
    passfile = certdir + "/passphrase"
    outcert  = certdir + "/newcerts/" + client + ".cert.pem"

    # Show us what you've got
    print("sign_csr: openssl conf: %s" % csrconf)
    print("sign_csr: signed_cert: %s" % outcert)
    print("sign_csr: csr_file: %s" % csrfile)

    if os.path.isfile(outcert):
        print("sign_csr: Deleting existing certificate, %s." % outcert)
        os.unlink(outcert)

    # Check that we can create the CSR before signing it
    try:
        fh = open(csrfile ,"wb")
        fh.write( csr )
        fh.close()
    except FileNotFoundError as fnfe:
        print("sign_csr: CSR file, %s, doesn't exist or has zero size." % csrfile)
        abort(400)

    sign_cert = ("openssl ca -config %s -in %s   "
                 "-passin file:%s -batch -out %s "
                 "-extensions v3_req -extfile %s "
                 "-days 375 -notext -md sha256 "
                 % (csrconf, csrfile, passfile, outcert, csrconf) )

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
    #if( request.is_json == False ):
    #    return False
    # More validation
    return True

if __name__ == "__main__":
    app.run()
