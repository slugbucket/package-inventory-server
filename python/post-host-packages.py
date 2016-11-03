#!/usr/bin/env python
#
# Simple script to create a client object and transfer a set of packages to the
# (ruby rack-based) server.
# The package list should actually be in this code rather than the class
# file, but this is still early days.
#
from PackageInventoryClient import PackageInventoryClient

pic = PackageInventoryClient('localhost')
pic.hostname
pic.send_package_list()
