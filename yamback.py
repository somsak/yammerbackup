#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate backup of Yammer messages
Inspired by Python-Yammer-Oauth examples
"""

import os
from ConfigParser import ConfigParser
import webbrowser
import simplejson

from yammer.yammer import Yammer, YammerError


config_dir = os.path.join(os.path.expanduser('~'), '.yammerbackup')
if not os.path.exists(config_dir) :
    try :
        os.mkdir(config_dir)
    except :
        import traceback
        traceback.print_exc()
config_file = os.path.join(config_dir, 'config')

try:
    from local_settings import *
except ImportError:
    pass

config = ConfigParser()
config.read(config_file)

access_token_key = ''
access_token_secret = ''
if config.has_section('main') :
    if config.has_option('main', 'access_token_key') :
        access_token_key = config.get('main', 'access_token_key')
    if config.has_option('main', 'access_token_secret') :
        access_token_secret = config.get('main', 'access_token_secret')

def get_proxy_info():
    """ Ask user for proxy information if not already defined in
    configuration file.

    """
    # Set defaults
    proxy = {'host': None,
             'port': None,
             'username': None,
             'password': None}

    if not use_proxy :
        return proxy

    # Is proxy host set? If not, ask user for proxy information
    if 'proxy_host' not in globals():
        proxy_yesno = raw_input("Use http proxy? [y/N]: ")
        if proxy_yesno.lower()[0:1].strip() == 'y':
            proxy['host'] = raw_input("Proxy hostname: ")
            port = raw_input("Proxy port: ")
            if not port:
                port = 80
            proxy['port'] = int(port)
            proxy['username'] = raw_input("Proxy username (return for none): ")
            if len(proxy['username']) != 0:
                proxy['password'] = raw_input("Proxy password: ")
    elif proxy_host:
        if 'proxy_port' not in globals():
            proxy['port'] = 80

    return proxy

def get_consumer_info():
    """ Get consumer key and secret from user unless defined in
    local settings.

    """
    consumer = {'key': None,
                'secret': None}
    if ('consumer_key' not in globals()
            or not consumer_key
            or 'consumer_secret' not in globals()
            or not consumer_secret):
        print "\n#1 ... visit https://www.yammer.com/client_applications/new"
        print "       to register your application.\n"

        consumer['key'] = raw_input("Enter consumer key: ")
        consumer['secret'] = raw_input("Enter consumer secret: ")
    else:
        consumer['key'] = consumer_key
        consumer['secret'] = consumer_secret

    if not consumer['key'] or not consumer['secret']:
        print "*** Error: Consumer key or (%s) secret (%s) not valid.\n" % (
                                                        consumer['key'],
                                                        consumer['secret'])
        raise StandardError("Consumer key or secret not valid")

    return consumer

#
# Main
#

yammer = None
proxy = get_proxy_info()
consumer = get_consumer_info()

# If we already have an access token, we don't need to do the full
# OAuth dance
if not access_token_key or not access_token_secret :
    try:
        yammer = Yammer(consumer['key'],
                        consumer['secret'],
                        proxy_host=proxy['host'],
                        proxy_port=proxy['port'],
                        proxy_username=proxy['username'],
                        proxy_password=proxy['password'])
    except YammerError, m:
        print "*** Error: %s" % m.message
        quit()

    print "\n#2 ... Fetching request token.\n"

    try:
        unauth_request_token = yammer.fetch_request_token()
    except YammerError, m:
        print "*** Error: %s" % m.message
        quit()

    unauth_request_token_key = unauth_request_token.key
    unauth_request_token_secret = unauth_request_token.secret

    try:
        url = yammer.get_authorization_url(unauth_request_token)
    except YammerError, m:
        print "*** Error: %s" % m.message
        quit()

    print "#3 ... Manually authorize via url: %s\n" % url
    webbrowser.open(url)

    oauth_verifier = raw_input("After authorizing, enter the OAuth "
                               "verifier (four characters): ")

    print "\n#4 ... Fetching access token.\n"

    try:
        access_token = yammer.fetch_access_token(unauth_request_token_key,
                                                 unauth_request_token_secret,
                                                 oauth_verifier)
    except YammerError, m:
        print "*** Error: %s" % m.message
        quit()

    access_token_key = access_token.key
    access_token_secret = access_token.secret

    print "Your access token:\n"
    print "Key:    %s" % access_token_key
    print "Secret: %s" % access_token_secret
    if not config.has_section('main') :
        config.add_section('main')
    config.set('main', 'access_token_key', access_token_key)
    config.set('main', 'access_token_secret', access_token_secret)
    f = open(config_file, 'w')
    config.write(f)
    f.close()

if 'username' not in globals():
    username = raw_input("Enter Yammer username (or return for "
                         "current): ")

#if 'include_replies' not in globals():
#    include_replies_yesno = raw_input("Include replies? [y/N]: ")
#    if string.strip((include_replies_yesno.lower())[0:1]) == 'y':
#        include_replies = True
#    else:
#        include_replies = False

print "\n#5 ... Fetching latest user post.\n"

# If we just got our access key, we already have a Yammer instance
if not yammer:
    try:
        yammer = Yammer(consumer['key'],
                        consumer['secret'],
                        access_token_key=access_token_key,
                        access_token_secret=access_token_secret,
                        proxy_host=proxy['host'],
                        proxy_port=proxy['port'],
                        proxy_username=proxy['username'],
                        proxy_password=proxy['password'])
    except YammerError, m:
        print "*** Error: %s" % m.message
        quit()

from output.sqlite import output

try:
#    r = yammer.get_user_posts(max_length=1,
#                              username=username,
#                              include_replies=True)

    out = output(output_url)

    last_id = None
    last_id = out.get_min_id()
    print "Last ID = ", last_id
    while True :
        messages = yammer.get_messages(older_than = last_id)

        if not messages: 
            break

        for m in messages :
            if not last_id or (last_id > m['id']) :
                last_id = m['id']
            out.put(m)
        out.commit()

    yammer.close()
    #print "Result:"
    #print simplejson.dumps(r, indent=4)
except YammerError, m:
    print "*** Error: %s" % m.message
    quit()
