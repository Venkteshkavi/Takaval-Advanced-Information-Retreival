# -*- coding: utf-8 -*-

#==========I.Basic Configuration Begins==========#

##################################################
##############A.BUILTIN CONFIGS###################
##################################################

# Enable/Disable debug mode in Flask
DEBUG = True
# Enable/Disable testing mode in Flask
TESTING = False
# The secret key for the Flask App
SECRET_KEY = '3912e802-a02c-11e7-abf4-780cb8781d2e'
#Enable/Disable Assets Debugging in Flask
ASSETS_DEBUG = True

##################################################
##############B.CUSTOM CONFIGS####################
##################################################

HOST_BASE_LINK = "http://localhost:5000"

###Extensions Allowed###

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG', 'PDF', 'pdf'])


#=========I.Database Configuration Begins========#

##################################################
##################A.MYSQL DB######################
##################################################

# MySQL credentials for connection
# Needs valid Host Server, database name, User name
# and password to make a connection
# Install MySQL-python
# default mysql port is 3306

DB_PASS="takaval@137" #Database Security Password
DB_USER_NAME="root" #Database User Name
DB_NAME="takaval" #Name of the Database Used
DB_SERVER_NAME="mysql" #Name of the Host Server or IP Adderss

#==========Database Configuration Ends==========#