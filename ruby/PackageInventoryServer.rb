#!/usr/bin/env ruby
#
# Simple server to receive a list of installed packages and their version
# Clients are intended to run on host systems and fire across some YAML
# in the following format
#
# ...

class PackageInventoryServer
  attr_reader :hosts, :supported_oses, :hosts_packages
  STRICT_HOST_MATCHING = nil

  def initialize
    @supported_oses = %w(centos antergos)
    @hosts_packages = Hash.new
  end

  # Method to register the package data for a host. The JSON input is
  # parsed to an array and the JSON data is written to a file for later
  # retrieval.
  # params
  #  reqhost: string: the name of the requesting host from the request headers
  #  jdata: string: JSON object
  # returns
  #  integer: number of packages in the array
  def add_host( reqhost, jdata )
    # Check that we have some valid data
    return nil if ! validate_package_list jdata

    host = JSON.parse(jdata)['hostname']

    if (STRICT_HOST_MATCHING && host != reqhost.chop)
      STDERR.print "ERROR: Client name #{host} does not match package list node, #{reqhost}."
      return 0
    end

    hosts[host] = Hash.new
    packages = JSON.parse( jdata )['packages']
    @hosts_packages[host] = packages
    pnum = packages.count

    save_host host, jdata
    return pnum
  end

  # Method to return an array containing the packages for a host.
  # If the host's array entry is not alredy in memory, attemp to read it
  # from file
  # params
  #  hostname: string: the name of the host
  def get_packages hostname
    return nil if ! hostname

    if ! @hosts_packages[hostname] then
      @hosts_packages[hostname] = read_host hostname
    end
    @hosts_packages[hostname]
  end

  # Method to flush a host's package entries
  # params:
  #  hostname: string
  # returns
  #  true or nil
  def flush_host hostname
    if @hosts_packages[hostname] then
      @hosts_packages.delete hostname
      return true
    else
      return nil
    end
  end
  # Method to return the number of packages available for the host
  # params
  #  hostname: string: the name of the host
  # returns
  #  integer: size of the packages array entry for the host
  def package_count hostname
    return 0 if ! hostname
    @hosts_packages[hostname] = read_host( hostname ) if ! @hosts_packages[hostname]
    return @hosts_packages[hostname].count || 0
  end
  private

  # Method to return an array in response for the requested host of the form
  # params:
  #   hostname: string
  # returns: array or nil
  def read_host hostname
    begin
     jdata = File.read( "cache/#{hostname}" )
   rescue Errno::ENOENT => e
     return nil
   end
    if validate_package_list( jdata ) then
      return JSON.parse( jdata )["packages"]
    end
    return nil
  end

  # Hack method to save the contents of the package list to a file named after
  # the host
  # params
  #  host: string: name of host data to be saved
  #  jdata: string: JSON object
  # returns
  #  void
  def save_host host, jdata
    File.open("cache/#{host}", "w") do |c|
      c.write jdata
    end
  end

  # Simple method to validate the data to be written to teh cache or returned
  # to the client
  def validate_package_list doc
    begin
      json = JSON.parse doc
    rescue JSON::ParserError => e
      STDERR.print "JSON parse error: #{e}"
      return nil
    end
    return true

    # When we start to do some better validation
    return nil if ! json['packages']
    #jdata['packages'].map{|n, v| STDOUT.print "Package #{n} is at version #{v}."}
    #STDOUT.flush
  end
end

package_inventory = PackageInventoryServer.new

# route requesting details of a known host
get '/package-inventory/:hostname' do
  return_message = {}
  hostname = params[:hostname]
  pkgs = package_inventory.get_packages hostname
  if ! pkgs then
    status 404
    return_message[:status] = "Cannot find package list for #{params[:hostname]}"
    return "#{return_message.to_json}"
  end

    if pkgs.count > 0 then
      return_message[:packages] = package_inventory.get_packages( params[:hostname] )
      status 200
    else
      return_message[:status] = "Returned empty package list for #{params[:hostname]}"
      status 404
    end
    "#{return_message.to_json}"

end

# Accept a POST request to register a new host's packages
post '/package-inventory/packages/new' do
  return_message = {}

  # The request body is a StringIO object which means that it can be read as a
  # file stream, but tht means only accessed once via read!
  jd = request.body.read.to_s
  jdata = JSON.parse jd

  num = package_inventory.add_host( request.host, jd)
  if num > 0 then
    return_message[:status] = "Received #{num} packages for #{jdata['hostname']}."
    status 200
  else
    return_message[:status] = "Failed to register packages for #{request.host}."
    status 400
  end
  STDOUT.flush
  return_message.to_json
end

# Accept a request to delete a host's package entry, but leave the
# cache intact
post '/package-inventory/:hostname/delete' do
  return_message = {}

  hostname = params[:hostname]
  if package_inventory.flush_host hostname then
    return_message[:status] = "Deleted packages entry for #{hostname}"
    status 200
  else
    return_message[:status] = "Could not delete packages entry for #{hostname}"
    status 400
  end
  return_message.to_json
end
