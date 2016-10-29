#
# Test routines for Sinatra application using rack
# Based on an example at http://stackoverflow.com/questions/2055933/how-do-you-run-tests-in-sinatra
# Run the tests using,
# ruby PackageInventoryServerTest.rb
ENV['RACK_ENV'] = 'test'

require 'rubygems'
require 'sinatra'
root = ::File.dirname(__FILE__)
require ::File.join( root, 'PackageInventoryServer' )
require 'test/unit'
require 'rack/test'
require 'json'

configure :production, :test, :development do
  enable :logging, :dump_errors, :raise_errors
  logger = ::File.open("log/test.log", "a+")
end
set :run, true
set :show_exceptions, true if :test?
set :port, 4568
set :environment, :test

class PackageInventoryServerTest < Test::Unit::TestCase
  include Rack::Test::Methods

  def app
    Sinatra::Application
  end

  # Test to verify that we get a failure when we issue a request for a missing resource
  # We need to ensure that there is no reference to the packages for out test host
  # when we make the request for failure
  def test_get_host_packages_fail
    hostname = "invtest"

    puts "Flushing package entry for #{hostname}"
    headers = { 'CONTENT_TYPE' => 'application/json' }
    json = '{"hostname": "invtest"}'
    post "/package-inventory/#{hostname}/delete", json, headers
    assert_equal 200, last_response.status
    assert_equal "{\"status\":\"Deleted packages entry for #{hostname}\"}", last_response.body

    puts "Removing cache file for #{hostname} if it exists."
    File.delete("cache/#{hostname}") if File.exists?("cache/#{hostname}")

    # Request that
    get "/package-inventory/#{hostname}"
    assert_equal 404, last_response.status
    expect = "{\"status\":\"Cannot find package list for #{hostname}\"}"
    assert_equal expect, last_response.body
  end

  # Test to post an entry to the server ready to be downloaded later
  def test_host_package_post
    hostname = "invtest"
    jdata = {}
    jdata[:hostname] = hostname
    jdata[:packages] = {}
    ["phonon-qt5-gstreamer 4.9.0", "my-package 1.2.3", "your-package 4.5.6-0.1"].each do |pkg|
      jdata[:packages].merge! Hash[*pkg.chop.split(/ /)]
    end

    request = '/package-inventory/packages/new'
    headers = { 'CONTENT_TYPE' => 'application/json' }
    post request, jdata.to_json, headers

    assert last_response.ok?
    assert_equal "{\"status\":\"Received 3 packages for invtest.\"}", last_response.body
  end
  # Test to verify that we get a success when we issue a request for a newly added resource
  def test_get_host_packages
    hostname = "invtest"
    get "/package-inventory/#{hostname}"
    assert_equal 200, last_response.status
    expect = "{\"packages\":{\"phonon-qt5-gstreamer\":\"4.9.\",\"my-package\":\"1.2.\",\"your-package\":\"4.5.6-0.\"}}"
    assert_equal expect, last_response.body
  end
end
