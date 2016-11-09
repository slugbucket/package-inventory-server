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
    self._distro = platform.linux_distribution()[0]

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

  # Method to determine which distro this is running on so that we can
  # know which package invemtory method to invoke
  #def distro():
    #  doc = "The Linux distribution name."
    #  def fget(self):
    #      return self._distro
    #  def fset(self, value):
    #      self._distro = value
    #  def fdel(self):
    #      del self._distro
    #  return locals()

  #distro = property(**distro())

  def get_packages(self):
      #print ( distro() )
      self._packages = {
        'Antergos Linux': self.pacman(),
        'b': True,
        'c': True
      }[self._distro]

  # Method to run a system command and save the output for processing
  def run_command(self, command):
      #p = subprocess.check_output(command.split(),
      p = subprocess.run(command.split(),
                           bufsize=1,
                           stdout=subprocess.PIPE)
                           #stderr=subprocess.STDOUT)
      #return iter(p.stdout.readline, b'')
      return( p.stdout )

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
  def _pacman_qi_split(self, pqi):
      print( "pacman_qi_split: splitting " + pqi)

  def pacman(self):
      print( "Getting ArchLinux packages.")
      #proc = subprocess.Popen(['/usr/bin/pacman', '-Qi'], stdout=subprocess.PIPE, bufsize=0)
      #tmp = proc.stdout().read()
      #pkgs = subprocess.Popen(["/usr/bin/pacman", "-Qi"], stdout=subprocess.PIPE).stdout().read()
      #for pkgi in pkgs:
      #    pass
      pkgs = self.run_command('/usr/bin/pacman -Qi docker-machine')
      pkg = ""
      for pkgi in pkgs.split( '\n', pkgs):
          print( "line: {}".format(pkgi))
          if( re.search( '^$', pkgi ) ):
              self._pacman_qi_split(pkg)
              pkg = ""
          else:
              pkg += pkgi

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
        resp = requests.post( "http://localhost:5000/package-inventory/packages/new", data=json.JSONEncoder().encode( jdata ) )
        print( "send_package_list: " + str( resp.text ) )

      except requests.exceptions as err:
          if err.HTTPError == 404:
              print( "Address not found." )
          else:
              print( "RestClient response: " + err.text + "." )
