# import the standard JSON parser
import json
# import the REST library
import requests
import subprocess
import platform
import re

class PackageInventoryClient:
  def __init__( self ):
    self._hostname = platform.node()
    self._distro   = platform.linux_distribution()[0]
    self.packages  = {}

  #def __init__( self, name ):
  #  self._hostname = name
  #self._distro = subprocess.call("cat /etc/issue | cut -d' ' -f1'").read()

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

  def get_packages(self, captions=('Name', 'Version', 'Description')):
      #print ( distro() )
      self.packages = {
        'Antergos Linux': self.pacman_qi(captions),
        'b': True,
        'c': True
      }[self._distro]

  # Method to extract package details from pacman -Qi <pkgnme>
  # typically looking like:
  #Name            : phonon-qt5-gstreamer
  #Version         : 4.9.0-1
  #Description     : Phonon GStreamer backend for Qt5
  #Architecture    : x86_64
  #URL             : http://phonon.kde.org/
  #Licenses        : LGPL
  #Groups          : None
  #Provides        : phonon-qt5-backend
  #Depends On      : gst-plugins-base  qt5-x11extras
  #Optional Deps   : pulseaudio: PulseAudio support [installed]
  #                  gst-plugins-good: PulseAudio support and good codecs
  #                  [installed]
  #                  gst-plugins-bad: additional codecs [installed]
  #                  gst-plugins-ugly: additional codecs [installed]
  #                  gst-libav: libav codec [installed]
  #Required By     : phonon-qt5
  #Optional For    : None
  #Conflicts With  : phonon-gstreamer
  #Replaces        : phonon-gstreamer
  #Installed Size  : 411.00 KiB
  #Packager        : Antonio Rojas <arojas@archlinux.org>
  #Build Date      : Mon 18 Apr 2016 08:03:24 BST
  #Install Date    : Sun 02 Oct 2016 18:57:59 BST
  #Install Reason  : Installed as a dependency for another package
  #Install Script  : No
  #Validated By    : Signature
  # We don't need all of these but we'll return an array containing
  # name, version, description, architecture, url, license
  #
  # written by mhrawcliffe
  def pacman_qi(self, captions):
      """
      Takes a multiline string as input

      Returns a list of dictionaries pertaining to the output
      with keys matching the captions passed as input.
      """
      output = subprocess.getoutput("pacman -Qi")
      packages = []
      # group packages together
      for package in output.split('\n\n'):
          caption = ""
          current_package = {}
          # each line in the package grouping
          for line in package.split('\n'):
              # match initial line e.g. Caption  : Info
              info = re.match(r'^([A-Za-z]+)\s*:\s+(.*)$', line)
              if info:
                  # if its a definition, add to the dict
                  caption = info.group(1)
                  current_package[caption] = info.group(2)
              else:
                  # is it a continuation of a caption,
                  # i.e. zuki-themes description 2nd line
                  info = re.match(r'^\s+(.*)$', line)
                  if info and caption:
                      # append the info to the respective caption
                      current_package[caption] += ' ' + info.group(1)
                  elif not caption:
                      # no caption has been defined so this is stray output
                      raise ValueError("Malformed pacman output")

          # add the related info to the packages list as a dict
          # with only relevant captions, using a dict comprehension
          packages.append({
              caption: value for caption, value in current_package.items()
              if caption in captions
          })

      return packages

  # Bundle up the list of packages in to the following format
  # {"packages": [{"phonon-qt5-gstreamer": "4.9.0"}, {"my-package": ...}
  def send_package_list(self):
      jdata = {}
      jdata['hostname'] = self._hostname
      jdata['packages'] = self.packages

      try:
        resp = requests.post( "http://localhost:5000/package-inventory/packages/new", data=json.JSONEncoder().encode( jdata ), headers={'Content-Type': 'application/json'})
        print( "send_package_list: " + str( resp.text ) )

      except requests.exceptions as err:
          if err.HTTPError == 404:
              print( "Address not found." )
          else:
              print( "RestClient response: " + err.text + "." )
