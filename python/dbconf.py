#
# Establish  connection to the database
#
import mysql.connector
from mysql.connector import errorcode

def dbconnect():
    dbuser='db-user'
    dbpass='db-passwd'
    dbhost='127.0.0.1'
    database='the-database'
    cnx = None

    try:
        cnx = mysql.connector.connect(user=dbuser,
                                      password=dbpass,
                                      host=dbhost,
                                      database=database)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            cnx.close()
    return( cnx )
