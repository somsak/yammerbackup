#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Local settings for example.py
#
# Change filename to example_local_settings.py
#

delay = 60

# If consumer key and secret are commented out, None, or '',
# instructions will be given on how to obtain them.
#
consumer_key = 'wNk0XsH7FNirMMJsUnPu2w'
consumer_secret = 'gF9G7PR8cshx7nsgaB46wAzKgT1SyxkATCSRXXU5VLg'

# If access token key and secret are commented out, None or '',
# instructions will be given on how to obtain them.
#
# access_token_key = ''
# access_token_secret = ''

# If proxy settings are commented out, the user will be asked for
# the information. User and password is optional. Set proxy_host to
# None if you don't want to use a proxy server.
#
# proxy_host = ''
# proxy_port = 8080
# proxy_username = ''
# proxy_password = ''

# Username can be set to a name of a user to get that user's timeline
# instead of the user who owns the access token. If commented out, set
# to None or '', the user will be asked for this information.
#
username = 'somsak'

# Whether or not to include replies in the result set. If commented out,
# set to None or '', the user will be asked for this information.
#
# include_replies = False

use_proxy = False

output_driver = 'output.sqlite'
output_url = 'sqlite:////home/somsak/Desktop/yammer.sqlite'
#output_url = 'sqlite:///:memory:'
