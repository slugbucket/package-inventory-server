require 'sinatra'
require 'rubygems'
require 'json'

root = ::File.dirname(__FILE__)
require ::File.join( root, 'PackageInventoryServer' )

# Sinatra setup
set :environment, :development
logger = ::File.open("log/development.log", "a+")

# Development environment configuration
configure :development do
  enable :logging, :dump_errors, :raise_errors
end

# Configuration for the test environment
configure :test do
  enable :logging, :dump_errors, :raise_errors
  logger = ::File.open("log/test.log", "a+")
  set :port, 4567
  set :show_exceptions
end

# Production environment configuration
configure :production do
  enable :logging, :dump_errors, :raise_errors
  logger = ::File.open("log/production.log", "a+")
end
set :run, true
set :port, 4567 if :development
# set :port, 4567 if :test
set :show_exceptions, true if development?

STDOUT.reopen(logger)
STDERR.reopen(logger)
use Rack::CommonLogger, logger

run PackageInventoryServer.new
