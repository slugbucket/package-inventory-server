#!/usr/bin/env ruby
#
# Simple service to request a list of installed packages and their version
#

require 'json'
require 'rest-client'

class PackageInventoryClient
  @@flds

  def initialize
    @packages = Hash.new
    @packages[:hostname] = `hostname`.chomp
  end

  # Method to be run on Arch Linux to probe read the local packages and extract
  # the fields we are interested in. The format of pacman -Qi output is like
  # Name           : zita-alsa-pcmi
  # Version        : 0.2.0-3
  # The RE match relies on there being at least two spaces before the :
  # params:
  #  None
  # returns:
  #  Array of hashes each of the form: {field1 => val1, field2 => val2, ...}
  def pacman_qi
    #pattern = /(.*)\b([ ]{2,}:) (.*)$/
    pattern = /(.*)\b[ ]{2,}: (.*)$/
    pkg     = {}
    jdata   = []

    pkgs = open("|/usr/bin/pacman -Qi docker-machine zuki-themes alsa-utils alsa-plugins alsa-lib").each do |pkgline|
      if pkgline.match(/^$/) then
        jdata << pkg
        pkg = {}
      end
      pkgline.gsub!( pattern ) do
        pkg[$1] = $2 if @@flds.include?($1)
      end
    end
    return jdata
  end

  # Method to get determine the command to retrieve the package details
  # and extract the requested fields (where available from the output)
  # params:
  #   fields: Array containing names of fields - ['Name', 'Version', 'Description']
  # returns:
  #   0 (success) or nil
  def get_packages( fields = [] )
    @@flds = fields if fields.kind_of?(Array)

    @packages[:packages] = pacman_qi()
    puts @packages[:packages].to_json
  end

  # Bundle up the list of packages in to the following format
  #  {"hostname":"invtest",
  #    "packages":[
  #      {"Name":"docker-machine","Version":"0.8.2-1","Description":"Machine management for a container-centric world","Architecture":"x86_64","URL":"https://github.com/docker/machine"},
  #      {"Name":"zuki-themes","Version":"20150516-1","Description":"Zuki themes for GTK3, GTK2, Metacity, xfwm4, Gnome Shell and Unity.","Architecture":"any","URL":"https://github.com/lassekongo83/zuki-themes/"}
  #    ]
  #  }
  def send_package_list
    begin
      resp = RestClient.post "http://localhost:4567/package-inventory/packages/new", @packages.to_json, :content_type => :json, :accept => :json

      STDOUT.print "send_package_list: #{resp.body}"
    rescue RestClient::BadRequest, RestClient::InternalServerError => e
      STDOUT.print "RestClient response: #{e.response}"
    puts "and ends here"
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
pic.get_packages(['Name', 'Version', 'Description', 'Architecture', 'URL'])
pic.send_package_list
