#!/usr/bin/env ruby
#
# Simple service to request a list of installed packages and their version
#

require 'json'
require 'rest-client'

class PackageInventoryClient
<<<<<<< HEAD
=======
  #attr_reader :hostname
>>>>>>> 93b07321e60ba220cdb674da30fb4800fdc3d396
  @@flds

  def initialize
    @packages = Hash.new
    @packages[:hostname] = `hostname`.chomp
  end

  # Method to be run on Arch Linux to probe read the local packages and extract
  # the fields we are interested in
  # params:
  #  None
  # returns:
  #  Array of hashes each of the form: {field1 => val1, field2 => val2, ...}
  def pacman_qi
    pattern = /(.*)\b([ ]{2,}:) (.*)$/
    pkg = {}
    jdata = []

    pkgs = open("|/usr/bin/pacman -Qi docker-machine zuki-themes").each do |pkgline|
      if pkgline.match(/^$/) then
        jdata << pkg
        pkg = {}
      end
      pkgline.gsub!( pattern ) do
        k = $1
        v = $3
        #puts "pacman_qi: Saving pkg setting #{k} with value #{v}" if @@flds.include?(k)
        pkg[k] = v if @@flds.include?(k)
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
<<<<<<< HEAD
    @@flds = fields if fields.kind_of?(Array)

    @packages[:packages] = pacman_qi()
    #puts @packages[:packages].to_json
=======
    #@packages = {}
    #@packages[:hostname] = `hostname`.chomp
    @@flds = fields if fields.kind_of?(Array)

    puts "Getting packages for #{@packages[:hostname]}"
    @packages[:packages] = pacman_qi()
    puts @packages[:packages].to_json
>>>>>>> 93b07321e60ba220cdb674da30fb4800fdc3d396
  end

  # Bundle up the list of packages in to the following format
  #  {"hostname":"invtest",
  #    "packages":[
  #      {"Name":"docker-machine","Version":"0.8.2-1","Description":"Machine management for a container-centric world","Architecture":"x86_64","URL":"https://github.com/docker/machine"},
  #      {"Name":"zuki-themes","Version":"20150516-1","Description":"Zuki themes for GTK3, GTK2, Metacity, xfwm4, Gnome Shell and Unity.","Architecture":"any","URL":"https://github.com/lassekongo83/zuki-themes/"}
  #    ]
  #  }
  def send_package_list
<<<<<<< HEAD
    begin
=======
    # Move this to get_packages
    #jdata = {}
    #jdata[:hostname] = `hostname`.chop
    #jdata[:hostname] = "invtest"
    #jdata[:packages] = pacman_qi()
    #puts jdata.to_json
    begin
      #resp = RestClient.post "http://localhost:4567/package-inventory/packages/new", jdata.to_json, :content_type => :json, :accept => :json
   puts "action starts here"
>>>>>>> 93b07321e60ba220cdb674da30fb4800fdc3d396
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
