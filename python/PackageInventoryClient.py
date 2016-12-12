# import the standard JSON parser
import json
# import the REST library
import requests
import subprocess
import platform
import re
import os
import OpenSSL

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

  def create_csr(self, common_name, country=None, state=None, city=None,
               organization=None, organizational_unit=None,
               email_address=None):
    """
    Method to create a request for a new client certificate
    Taken from http://stackoverflow.com/questions/3215780/generating-a-csr-in-python
    Args:
        common_name (str).
        country (str).
        state (str).
        city (str).
        organization (str).
        organizational_unit (str).
        email_address (str).
    Returns:
        (str, str).  Tuple containing private key and certificate
        signing request (PEM).
    """
    print("create_csr: generating certificate request.")
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

    req = OpenSSL.crypto.X509Req()
    req.get_subject().CN = common_name
    if country:
        req.get_subject().C = country
    if state:
        req.get_subject().ST = state
    if city:
        req.get_subject().L = city
    if organization:
        req.get_subject().O = organization
    if organizational_unit:
        req.get_subject().OU = organizational_unit
    if email_address:
        req.get_subject().emailAddress = email_address

    req.set_pubkey(key)
    req.sign(key, 'sha256')

    private_key = OpenSSL.crypto.dump_privatekey(
        OpenSSL.crypto.FILETYPE_PEM, key)

    csr = OpenSSL.crypto.dump_certificate_request(
               OpenSSL.crypto.FILETYPE_PEM, req)

    #print("create_csr: Generated CSR: %s" % str(csr, 'utf-8'))

    return private_key, str(csr, 'utf-8')

  def send_cert_request(self, hostname = None):
      (privkey, csr) = self.create_csr(hostname, 'GB', 'Denial', 'Hometown',
              'Package Inventory Services', 'Our Department', '')
      #jdata = {"hostname": hostname, "csr": csr}
      #resp = requests.post( "http://localhost:5000/package-inventory/client-cert/new", data=json.JSONEncoder().encode( jdata ), headers={'Content-Type': 'application/json'})
      try:
          resp = requests.post( "http://localhost:5000/package-inventory/client-cert/new", data=csr, headers={'Content-Type': 'application/pkcs10'})
      except requests.exceptions.ConnectionError as connerr:
          print("send_cert_request: Connection error: %s" % connerr)
          exit(1)
      else:
          print("send_cert_request: save cert from %s" % resp)
          if resp.status_code == 200:
              cc = resp.text
              print("send_cert_request: received cert.")
              self.save_client_cert(hostname, "ssl", privkey, resp.text)
          else:
              print("send_cert_request: cert request failed with %s [%s]" % (resp.text, str(resp.status_code)))
              return(False)
      return(True)

  def fetch_client_cert(self, hostname = None, cdir = "."):
      """
      Method to get the local client certificate
      params:
       hostname: String: fully qualifies name of the requesting client
       dir: String: the location of the certificate
      Returns:
       String|None: Contents of client certificate, if exists; None if not
      """
      print("fetch_client_cert: Looking for client cert in %s/%s" % (cdir, hostname))
      fn = "%s/%s.cert.pem" % (cdir, hostname)
      print("fetch_client_cert: Expect to find client cert at %s." % fn)
      if os.path.isfile(fn):
          fh = open(fn ,"r")
          #print("fetch_client_cert: Read %s from %s certificate"% (fh, hostname))
          cert = fh.read()
      else:
          # Generate a CSR and send a signing request
          print("fetch_client_cert: Sending CSR.")
          cert = self.send_cert_request("fnunbob.localdomain")

      return(cert)

  def save_client_cert(self, hostname = None, cdir = ".", key = None, cert = ""):
      """
      Method to save the local client certificate
      params:
       hostname: String: fully qualifies name of the requesting client
       dir: String: the location of the certificate
       key: the private key to match the certificate
       cert: The signed certificate from the CA
      Returns:
       True|False: Successfully saved cert/key (True); False otherwise
      """
      print("save_client_cert: Saving key in %s/%s" % (cdir, hostname))
      print(key)
      fn = "%s/%s.key.pem" % (cdir, hostname)
      fh = open(fn ,"w")
      fh.write(str(key))
      fh.close()

      print("save_client_cert: Saving client cert in %s/%s" % (cdir, hostname))
      print(cert)
      fn = "%s/%s.cert.pem" % (cdir, hostname)
      fh = open(fn ,"w")
      fh.write(cert)
      fh.close()
      return(True)

  def get_packages(self, captions=('Name', 'Version', 'Description')):
      """
      Method to identify what distribution command needs to be run to get
      the list of installed packages.
      The retrieved details are saved to an instance variable
      Params:
        captions: Array: package attribute headings to retrieve
      Returns:
        void
      """
      if self._distro == 'arch':
          print("get_packages: Fetching ArchLinux list.")
          self.packages = self.pacman_qi(captions)
      elif self._distro == 'debian':
          print("Fetching debian package list.")
          self.packages = self.dpkg_l(captions)
      else:
          return []

  def dpkg_l(self, captions):
      """
      Method to extract package details from dpkg -l
      typically in the format
      ii  acl                                 2.2.52-2                   armhf        Access control list utilities
      ii  adduser                             3.113+nmu3                 all          add and remove users and groups
      The format of dpkg output is such that we can't use the captions to
      match against the package value; on raspbian at least, dpkg-query --show --showformat "..." doesn't give any output
      params:
        captions: Array: Headings for values to be captured
      returns:
       Array of dicts containing keys and values for each package
      """
      packages = []
      output = subprocess.getoutput("dpkg -l")
      for pkgline in output.split('\n'):
          patt = re.compile('ii\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(.*)')
          pary = patt.match(pkgline)
          if pary:
              packages.append({ 'Name': pary.group(1), 'Version': pary.group(2), 'Architecture': pary.group(3), 'Description':  pary.group(4) })
              #print( json.JSONEncoder().encode( { 'Name': pary.group(1), 'Version': pary.group(2), 'Architecture': pary.group(3), 'Description':  pary.group(4) } ) )
          else:
              print("No match found for " + pkgline + ".")

      print("Sending " + str( len(packages)) + " to server")
      return(packages)


  def pacman_qi(self, captions):
      """
      Method to extract package details from pacman -Qi <pkgnme>
      typically looking like:
        Name            : phonon-qt5-gstreamer
        Version         : 4.9.0-1
        Description     : Phonon GStreamer backend for Qt5
        Architecture    : x86_64
        URL             : http://phonon.kde.org/
        Licenses        : LGPL
        Groups          : None
        Provides        : phonon-qt5-backend
        Depends On      : gst-plugins-base  qt5-x11extras
        Optional Deps   : pulseaudio: PulseAudio support [installed]
                          gst-plugins-good: PulseAudio support and good codecs
                          [installed]
                          gst-plugins-bad: additional codecs [installed]
                          gst-plugins-ugly: additional codecs [installed]
                          gst-libav: libav codec [installed]
        Required By     : phonon-qt5
        Optional For    : None
        Conflicts With  : phonon-gstreamer
        Replaces        : phonon-gstreamer
        Installed Size  : 411.00 KiB
        Packager        : Antonio Rojas <arojas@archlinux.org>
        Build Date      : Mon 18 Apr 2016 08:03:24 BST
        Install Date    : Sun 02 Oct 2016 18:57:59 BST
        Install Reason  : Installed as a dependency for another package
        Install Script  : No
        Validated By    : Signature
      We don't need all of these but we'll return an array containing
      name, version, description, architecture, url, license

         written by mhrawcliffe
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

  def send_package_list(self):
      """
       Bundle up the list of packages in to the following format
      {"packages": [{"name": "phonon-qt5-gstreamer", "version": "4.9.0", "architecture": "x86_64", "description": "GStreamer package"}, ...]}
      params:
        None
      Returns:
        void
      """
      jdata = {}
      jdata['hostname'] = self._hostname
      jdata['packages'] = self.packages

      cc = self.fetch_client_cert("fnunbob.localdomain", "ssl")
      print("send_package_list: loaded certificate for %s." % jdata['hostname'])
      if(cc):
          print("send_package_list: Found certificate for %s." % self._hostname)
          print("send_package_list: Sending packages: %s" % jdata['packages'])
      else:
          print("send_package_list: Error:  Missing client cert for %s." % self._hostname)
          exit(1)

      try:
        resp = requests.post( "https://inventory-master.localdomain/package-inventory/packages/new", data=json.JSONEncoder().encode( jdata ), headers={'Content-Type': 'application/json'}, verify=False)
        #resp = requests.post( "http://localhost:5000/package-inventory/packages/new", data=json.JSONEncoder().encode( jdata ), headers={'Content-Type': 'application/json'})
        print( "send_package_list: " + str( resp.text ) )

      except requests.exceptions.HTTPError as err:
          print( "RestClient response: " + err.text + "." )
      except requests.exceptions.ConnectionError as connerr:
          print("RestClient connection error: Connection refused")
