# import the standard JSON parser
import json
# import the REST library - very old, don't use
# from restful_lib import Connection
# http://docs.python-requests.org/en/master/
import requests

# Database connection details stored separately
import dbconf
cnx = dbconf.dbconnect()

def add_package( dbh = None, name = None ):
    insert = ( "INSERT INTO packages(name, description, created_at, updated_at) "
               "VALUES( %s, 'Auto-discovered package', NOW(), NOW())" )
    dbh.execute( insert, ( name, ) )
    print( "add_package: Added package, %s" % name )

def add_package_version( dbh = None, name = None, pkg = None ):
    insert = ( "INSERT INTO package_versions( "
               "name, package_id, package_architecture_id, created_at, updated_at ) "
               "SELECT %s, p.id, pa.id, NOW(), NOW() "
               "FROM packages p, package_architectures pa "
               "WHERE p.name = %s "
               "AND pa.name = 'Unknown'")
    dbh.execute( insert, ( name, pkg ) )
    print( "add_package_version: Added package version, %s" % name )

def add_host_package_version( dbh = None, host = None, version = None ):
    insert = ("INSERT INTO host_package_versions(host_id, package_version_id) "
              "SELECT h.id, pv.id "
              "FROM hosts h, package_versions pv "
              "WHERE h.name = %s AND pv.name = %s")
    dbh.execute( insert, ( host, version ) )
    print( "add_host_package_version: Added host package version for %s" % host )

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
# (1, 1, 1): version of the package is installed on the host: associate version with host
# (0, 1, 1): version of the package exists but is not installed: create new version
# (0, 0, 1): version of the package does not exist: create new version
# (0, 0, 0): no reference to package in database: create package, version and host mapping
pkgqry = (
    "SELECT SUM(hostcount) AS hpv, SUM(pvcount) AS pv, SUM(pkgcount) AS p "
    "FROM "
    "(SELECT COUNT(h.id) AS hostcount, "
    "        0 AS pvcount, "
    "        0 AS pkgcount "
    "FROM hosts h "
    "  INNER JOIN host_package_versions hpv "
    "  ON h.id = hpv.host_id "
    "  INNER JOIN package_versions pv "
    "    ON hpv.package_version_id = pv.id "
    "  INNER JOIN packages p "
    "    ON pv.package_id = p.id "
    "WHERE h.name  = %s "
    "  AND pv.name = %s "
    "  AND p.name  = %s "
    "UNION "
    "SELECT 0 AS hostcount, "
    "       COUNT(pv.id) AS pvcount, "
    "       0 AS pkgcount "
    "FROM package_versions pv "
    "  INNER JOIN packages p "
    "    ON pv.package_id = p.id "
    "WHERE pv.name = %s "
    "  AND p.name  = %s "
    "UNION "
    "SELECT 0 AS hostcount, "
    "       0 AS pvcount, "
    "       COUNT(p.id) AS pkgcount "
    "FROM packages p "
    "WHERE p.name  = %s) AS t1" )

datacenter = "primary-dc"
cursor.execute(query, (datacenter, ) )
for (hostname, description) in cursor:
    url = "http://localhost:4567/package-inventory/" + hostname
    r = requests.get( url )

    if r.status_code == 200:
        print( r.text + " with status " + str( r.status_code ) )
        print( "name: {}, description: {}".format( hostname, description ) )
        js = json.loads( r.text )
        pkgs = js['packages']
        print( "packages are: " + str( pkgs ) )
        # process a list of the form
        # [{'phonon-qt5-gstreamer': '4.9.0'}, {'my-package': '1.2.3'}...]
        for p in pkgs:
          # Process the package components as single element dictionaries
          for pkg, vers in p.items():
            print( "package: %s, version: %s\n" % ( pkg, vers ) )
            try:
                pkgcur.execute( pkgqry, ( hostname, vers, pkg, vers, pkg, pkg) )
            except mysql.connector.Error as err:
                if err.errno == ER_INTERNAL_ERROR:
                    print( "Internal error: " + str( err.text) )
                elif err.errno == 1064:
                    print( "SQL error: " + str( err.text ))
                else:
                    print( "Database error (" + str( err.errno ) + "): " + str( err ) )

            for ( hpv, pv, p ) in pkgcur:
                print( "On host: %s, version exists: %s, package exists: %s.\n" % ( hpv, int( pv ), int( p ) ) )
                if int( p ) == 0:
                    add_package( pkgcur, pkg )
                if int( pv ) == 0:
                    add_package_version( pkgcur, vers, pkg )
                if int( hpv ) == 0:
                    add_host_package_version( pkgcur, hostname, vers )

cnx.commit()
pkgcur.close()

cursor.close()
cnx.close()
