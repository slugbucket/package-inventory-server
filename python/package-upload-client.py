# import the standard JSON parser
import json
# import the REST library - very old, don't use
# from restful_lib import Connection
# http://docs.python-requests.org/en/master/
import requests


r = requests.get( 'http://localhost:4567/package-inventory/invtest' )
print( r.text )
