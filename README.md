# package-inventory-server
client server applications for running a package inventory of servers and storing the results

It consists of two client-server services:
  - A data collector that receives a list of packages from client nodes on the network which are stored in local datastore,
  - A RESTful web server that reads the datastore and answers requests for node package lists from a service that stores the data in a (typically SQL) database.
The server and clients will be written in Ruby with the local datastore being YAML files.

Using https://www.sitepoint.com/uno-use-sinatra-implement-rest-api/ as a guide for using Sinatra and thin for the RESTful interface of the servers.
Also making good use of http://www.sinatrarb.com/intro.html
https://github.com/rest-client/rest-client

Sample data to be used for testing client submission:

{"hostname": "localhost", "packages": [{"a52dec": "0.7.4-9"},{"aalib": "1.4rc5-12"},{"accountsservice": "0.6.42-1"},{"acl": "2.2.52-2"},{"acpid": "2.0.28-1"},{"adwaita-icon-theme": "3.20-2"},{"alsa-lib": "1.1.2-1"},{"alsa-plugins": "1.1.1-1"},{"alsa-utils": "1.1.2-1"},{"antergos-gnome-defaults-list": "1.0-1"},{"antergos-keyring": "20150806-1"},{"antergos-mirrorlist": "20160821-1"},{"antergos-repo-priority": "1.0.4-2"},{"antergos-wallpapers": "0.6-2"},{"antergos-welcome": "0.0.2-2"}]}

This is my first attempt at writing something like a microservice.
