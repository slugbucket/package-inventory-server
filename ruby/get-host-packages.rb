#!/usr/bin/env ruby
#
# Simple service to request a retrieve the list of installed packages and their
# version from the package inventory server
# 

require 'json' 
require 'rest-client'

class PackageInventoryClient
  attr_reader :hostname

  def initialise name
    @hostname = name
  end
  
  # Prepare a bit of JSON from the package name and version
  def format_pkg_str pkg
    pkg
  end
  # Bundle up the list of packages in the following format
  #   {"<pkg-name>": "<pkg-vers>"}
  def get_package_list
    hostname = `hostname`.chop
    begin
      resp = RestClient.get "http://localhost:4567/package-inventory/#{hostname}", :accept => :json
      STDOUT.print "#{resp.body}"
    rescue RestClient::BadRequest, RestClient::InternalServerError => e
      STDOUT.print "#{e.response}"
    end
  end
end

pic = PackageInventoryClient.new
pic.get_package_list
