# import the standard JSON parser
import json
# import the REST library
import requests

class PackageInventoryClient:
  def __init__( self ):
    self._hostname = subprocess.call("/bin/hostname").read()

  def __init__( self, name ):
    self._hostname = name

  # Prepare a bit of JSON from the package name and version
  def format_pkg_str( pkg ):
    return( True )

  #def hostname( self ):
  #return( self.hostname )
  def gethostname(self):
      return( self._hostname )

  def sethostname(self, h):
      self._hostname = h

  def delhostname(self):
      del self._hostname

  hostname = property(gethostname, sethostname, delhostname, )

  # Bundle up the list of packages in to the following format
  # {"packages": [{"phonon-qt5-gstreamer": "4.9.0"}, {"my-package": ...}
  def send_package_list(self):
      jdata = {}
      jdata['hostname'] = self.hostname
      jdata['packages'] = []
      #pkgs = open("|pacman -Q").each do |pkg|
      pkglist = ["phonon-qt5-gstreamer 4.9.0", "my-package 1.2.3", "your-package 4.5.6-0.1"]
      for pkg in pkglist:
          (k, v) = pkg.split(" ")
          jdata['packages'].append( {k: v} )

      try:
        resp = requests.post( "http://localhost:4567/package-inventory/packages/new", data=json.JSONEncoder().encode( jdata ) )
        print( "send_package_list: " + str( resp.text ) )

      except requests.exceptions as err:
          if err.HTTPError == 404:
              print( "Address not found." )
          else:
              print( "RestClient response: " + err.text + "." )
