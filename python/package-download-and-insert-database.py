import unittest
import dbconf
from flask import Flask
from flask_testing import TestCase
import requests

class PackageInventoryServerTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_server_is_up_and_running(self):
        print("Testing that the server is up and running.\n")
        resp = requests.get("http://localhost:5000/")
        self.assertEqual(resp.status_code, 404)

    def test_get_host_packages_fail(self):
        print("Verify that a 404 is returned for non-existent resource.")
        resp = requests.get("http://localhost:5000/package-inventory/invtest")
        self.assertEqual(resp.status_code, 404)
        print(resp.json)

if __name__ == '__main__':
    unittest.main()

# We can probably replace this with SQLAlchemy
#cnx = dbconf.dbconnect()
#cnx.close()
