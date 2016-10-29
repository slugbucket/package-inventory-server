#!/usr/bin/env ruby
#
# Simple service to request a list of installed packages and their version
#

require 'json'
require 'rest-client'

class PackageInventoryClient
  attr_reader :hostname

  def initialise
    @hostname = `hostname`.chop
  end
  def initialise name
    @hostname = name
  end

  # Prepare a bit of JSON from the package name and version
  def format_pkg_str pkg
    pkg
  end
  # Bundle up the list of packages in to the following format
  #   <pkg-name>:
  #     version: <pkg-vers>
  def send_package_list
    jdata = {}
    #jdata[:hostname] = `hostname`.chop
    jdata[:hostname] = "invtest"
    jdata[:packages] = []
    pnum = 0
    #pkgs = open("|pacman -Q").each do |pkg|
    ["phonon-qt5-gstreamer 4.9.0", "my-package 1.2.3", "your-package 4.5.6-0.1"].each do |pkg|
      jdata[:packages] << Hash[*pkg.chomp.split(/ /)]
      pnum += 1
    end
    #json = json + "]}"
    puts jdata.to_json
    begin
      resp = RestClient.post "http://localhost:4567/package-inventory/packages/new", jdata.to_json, :content_type => :json, :accept => :json

      STDOUT.print "send_package_list: #{resp.body}"
    rescue RestClient::BadRequest, RestClient::InternalServerError => e
      STDOUT.print "RestClient response: #{e.response}"
    end
  end
  private
  # Method to split a two-word (space separated) string into a hash with the
  # first word as the key
  # http://stackoverflow.com/questions/39567/what-is-the-best-way-to-convert-an-array-to-a-hash-in-ruby
  # suggests a better way of doing this that doesn't require this method
  def str_to_hash str
    k, v = str.chop.split(/ /)
    {k.to_sym => v}
  end
end

pic = PackageInventoryClient.new
pic.send_package_list
