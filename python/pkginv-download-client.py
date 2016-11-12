#!/usr/bin/env python
#
# Script to query the inventory database for a list of hosts and for each
# one in the list submit a request to the package inventory server for the
# list of packages. We then go through the list of packages and update the
# host-package-version mapping as well as identifying whether new database
# entries are need for thr package and version

# import the standard JSON parser
import json
# import the REST library - very old, don't use
# from restful_lib import Connection
# http://docs.python-requests.org/en/master/
import requests

# Database connection details stored separately
import dbconf
cnx = dbconf.dbconnect()

# The package data returned by an invnetory request will be in teh form:
# [
#  {"Name":"docker-machine","Version":"0.8.2-1","Description":"Machine management for a container-centric world","Architecture":"x86_64","URL":"https://github.com/docker/machine"},
#  {"Name":"zuki-themes","Version":"20150516-1","Description":"Zuki themes for GTK3, GTK2, Metacity, xfwm4, Gnome Shell and Unity.","Architecture":"any","URL":"https://github.com/lassekongo83/zuki-themes/"}
# ]

# Method to add a new package record to the database
# params:
#  dbh: database handle
#  name: string: name of the package
#  descr: string: package descriptiom
# returns:
#   void
def add_package( dbh = None, name = None, descr = None ):
    insert = ( "INSERT INTO packages(name, description, created_at, updated_at) "
               "VALUES( %s, %s, NOW(), NOW())" )
    dbh.execute( insert, ( name, descr) )
    #print( "add_package: Added package, %s" % name )

# Method to add a new package version record to the database
# params:
#  dbh: database handle
#  name: string: version name of the package, 2.4.0-1.1
#  pkg: string: name of the package
#  arch: string: package architecture, e.g., x86_64, noarch, any, all
# returns:
#   void
def add_package_version( dbh = None, name = None, pkg = None, arch = None ):
    insert = ( "INSERT INTO package_versions( "
               "name, package_id, package_architecture_id, created_at, updated_at ) "
               "SELECT %s, p.id, pa.id, NOW(), NOW() "
               "FROM packages p, package_architectures pa "
               "WHERE p.name = %s "
               "AND pa.name = %s")
    dbh.execute( insert, ( name, pkg, arch ) )
    #print( "add_package_version: Added package version, %s" % name )

# Method to add a host mapping of a package version record to the database
# params:
#  dbh: database handle
#  host: string: name of teh host where package is installed
#  vers: string: name of the package version, e.g., 2.4.1-2.1
#  pkg: string: the name of the package, e.g., alsa-utils
# returns:
#   void
def add_host_package_version( dbh = None, host = None, vers = None, pkg = None ):
    insert = ("INSERT INTO host_package_versions(host_id, package_version_id) "
              "SELECT h.id, pv.id "
              "FROM hosts h, package_versions pv "
              "INNER JOIN packages p ON pv.package_id = p.id "
              "WHERE h.name = %s AND pv.name = %s AND p.name = %s")
    dbh.execute( insert, ( host, vers, pkg ) )
    #print( "add_host_package_version: Added host package version for %s" % host )

# Use buffered = True to avoid 'Unread result found' error
cursor = cnx.cursor()
pkgcur = cnx.cursor( buffered = True )

query = ("SELECT h1.name, h1.description FROM hosts h1 INNER JOIN locations l1 "
     "ON h1.location_id = l1.id WHERE l1.name = %s")

# Now see if there is a reference to the package an"d version in the
# database
# Get a count of the number of installs of the pack"age version on the hostname
# Anything over zero indicates it is installed
# There are four valid tuples we should receive from the query
# (1, 1, 1): version of the package is installed on the host: no action needed
# (0, 1, 1): version of the package exists but is not installed: create new association
# (0, 0, 1): version of the package does not exist: create new version
# (0, 0, 0): no reference to package in database: create package, version and host mapping
pkgqry = (
    "SELECT SUM(hostcount) AS hpv, SUM(pvcount) AS pv, SUM(pkgcount) AS p "
    "FROM "
    "(SELECT COUNT(h.id) AS hostcount, "
    "                  0 AS pvcount, "
    "                  0 AS pkgcount "
    "FROM hosts h "
    "  INNER JOIN host_package_versions hpv "
    "    ON h.id = hpv.host_id "
    "  INNER JOIN package_versions pv "
    "    ON hpv.package_version_id = pv.id "
    "  INNER JOIN packages p "
    "    ON pv.package_id = p.id "
    "WHERE h.name  = %s "
    "  AND pv.name = %s "
    "  AND p.name  = %s "
    "UNION "
    "SELECT            0 AS hostcount, "
    "       COUNT(pv.id) AS pvcount, "
    "                  0 AS pkgcount "
    "FROM package_versions pv "
    "  INNER JOIN packages p "
    "    ON pv.package_id = p.id "
    "WHERE pv.name = %s "
    "  AND p.name  = %s "
    "UNION "
    "SELECT           0 AS hostcount, "
    "                 0 AS pvcount, "
    "       COUNT(p.id) AS pkgcount "
    "FROM packages p "
    "WHERE p.name  = %s) AS t1" )

datacenter = "primary-dc"
cursor.execute(query, (datacenter, ) )
for (hostname, description) in cursor:
    url = "http://localhost:4567/package-inventory/" + hostname
    r = requests.get( url )

    if r.status_code == 200:
        #print( r.text + " with status " + str( r.status_code ) )
        js = json.loads( r.text )
        #pkgs = js['packages']
        #print( "packages are: " + str( pkgs ) )
        # process a list of the form
        # [{'phonon-qt5-gstreamer': '4.9.0'}, {'my-package': '1.2.3'}...]
        for p in js['packages']:
            #print( "The extracted package is " + str(p))
            # Process the package components as single element dictionaries
            #for pkg, vers, descr, arch, url in p.items():
            pkg  = p['Name']
            vers = p['Version']
            desc = p['Description']
            arch = p['Architecture']
            #print( "package: %s, version: %s, description: %s\n" % ( pkg, vers, desc ) )
            try:
                pass
                pkgcur.execute( pkgqry, ( hostname, vers, pkg, vers, pkg, pkg) )
            except mysql.connector.Error as err:
                if err.errno == ER_INTERNAL_ERROR:
                    print( "Internal error: " + str( err.text) )
                elif err.errno == 1064:
                    print( "SQL error: " + str( err.text ))
                else:
                    print( "Database error (" + str( err.errno ) + "): " + str( err.text ) )

            for ( hpv, pv, p ) in pkgcur:
                print( "On host: %s, version exists: %s, package exists: %s.\n" % ( hpv, int( pv ), int( p ) ) )
                if int( p ) == 0:
                    add_package( pkgcur, pkg, desc )
                if int( pv ) == 0:
                    add_package_version( pkgcur, vers, pkg, arch )
                if int( hpv ) == 0:
                    add_host_package_version( pkgcur, hostname, vers, pkg )
    else:
        print("Request failed with status: " + str(r.status_code))

cnx.commit()
pkgcur.close()

cursor.close()
cnx.close()
