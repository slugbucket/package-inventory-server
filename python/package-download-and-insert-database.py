import unittest
import dbconf
from flask import Flask
from flask_testing import TestCase
import os
import requests
import json

class PackageInventoryServerTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_03_host_package_post(self):
        jdata = {}
        jdata['hostname'] = "invtest"
        jdata['packages'] = [ { "Name": "phonon-qt5-gstreamer", "Version": "4.9.0", "Architecture": "x86_64", "Description": "GStreamer package", "URL": "http://www.anywhere.com/" }, { "Name": "my-package", "Version": "1.2.3", "Architecture": "noarch", "Description": "My great package", "URL": "http://www.overhere.com/my-package"}, { "Name": "your-package", "Version": "4.5.6-0.1", "Architecture": "any", "Description": "Your brilliant package", "URL": "http://www.overthere.com/your-package" } ]
        request = "http://localhost:5000/package-inventory/packages/new"
        try:
          resp = requests.post( request, data=json.JSONEncoder().encode( jdata ), headers={'Content-Type': 'application/json'})
          #print( "send_package_list: " + str( resp.text ) )
          self.assertEqual(resp.status_code, 200)
        except requests.exceptions as err:
            if err.HTTPError == 404:
                print( "Address not found." )
            else:
                print( "RestClient response: " + err.text + "." )

    def test_02_get_host_packages_fail(self):
        #print("Verify that a 404 is returned for non-existent resource.")
        resp = requests.get("http://localhost:5000/package-inventory/invtest")
        self.assertEqual(resp.status_code, 404)
        print(resp.json)

    def test_01_server_is_up_and_running(self):
        try:
            os.remove('cache/invtest')
        except OSError:
            pass
        #print("Testing that the server is up and running.\n")
        resp = requests.get("http://localhost:5000/")
        self.assertEqual(resp.status_code, 404)

    def test_04_get_host_packages_fail(self):
        #print("Verify that a 200 is returned after a new resource is created.")
        resp = requests.get("http://localhost:5000/package-inventory/invtest")
        self.assertEqual(resp.status_code, 200)
        print(resp.json)

if(__name__ == '__main__'):
    unittest.main()
#   We can probably replace this with SQLAlchemy
#   nx = dbconf.dbconnect()
#   nx.close()
