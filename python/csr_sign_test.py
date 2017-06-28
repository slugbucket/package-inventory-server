#!/usr/bin/env python
#
# http://stackoverflow.com/questions/23103878/sign-csr-from-client-using-ca-root-certificate-in-python - incomplete and bits that don't work but the general
# idea is resonable
# http://stackoverflow.com/questions/37120860/openssl-crypto-error-pem-routines-pem-read-bio-no-start-line
# http://blog.tunnelshade.in/2013/06/sign-using-pyopenssl.html - but the hashlib stuff doesn't work
# Get errors like: TypeError: Unicode-objects must be encoded before hashing
# Need to add .encode("utf-8") after the string
# http://stackoverflow.com/questions/7585307/typeerror-unicode-objects-must-be-encoded-before-hashing
#

from OpenSSL import crypto
import os, hashlib

def create_cert(caCert, deviceCsr, CAprivatekey):
    domain = "fnunbob.localdomain".encode("utf-8")

    md5_hash = hashlib.md5()
    md5_hash.update(domain)
    serial = int(md5_hash.hexdigest(), 36)

    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(notBeforeVal)
    cert.gmtime_adj_notAfter(notAfterVal)
    cert.set_issuer(caCert.get_subject())
    cert.set_subject(deviceCsr.get_subject())
    cert.set_pubkey(deviceCsr.get_pubkey())
    cert.sign(CAprivatekey, digest)
    return cert

#csr = crypto.load_certificate_request(crypto.FILETYPE_PEM, '/home/julian/Projects/python/client-cert-auth/cert-requests/fnunbob.localdomain.csr.pem')
csr_file = '/path/to/client-cert-auth/cert-requests/fnunbob.localdomain.csr.pem'
with open(csr_file, "r") as client_csr:
  csr_text = client_csr.read()
  csr = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr_text)

#privkey = crypto.load_privatekey('/home/julian/Projects/python/client-cert-auth/intermediate-ca/private/intermediate.key.pem')
key_file = '/path/to/client-cert-auth/intermediate-ca/private/intermediate.key.pem'
with open(key_file, "r") as private_key:
  key_text = private_key.read()
  privkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key_text)

cert_file = '/path/to/client-cert-auth/intermediate-ca/certs/ca-chain.cert.pem'
with open(cert_file, "r") as ca_cert:
  cert_text = ca_cert.read()
  ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_text)

signed_cert = create_cert(ca_cert, csr, privkey)
