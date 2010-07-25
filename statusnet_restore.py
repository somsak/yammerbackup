#/usr/bin/python

import sys, getpass

import MySQLdb

from local_settings import *
from output.sqlite import output

if len(sys.argv) < 4 :
    sys.exit(1)

username_map = {
    'pybt': 'piyaboot',
}

local_db = output(None, output_url)

BASE_STATUSNET_URL = 'http://status.inox.co.th'
db_host = sys.argv[1]
db_name = sys.argv[2]
db_user = sys.argv[3]

db_password = getpass.getpass('Password: ')

conn = MySQLdb.connect(db_host, db_user, db_password, db_name, use_unicode = True, charset='utf8')

c = conn.cursor()

# fetch list of profile from status.net first
c.execute('''SELECT id,nickname FROM profile''')

userid_map = {}
while True :
    row = c.fetchone()

    if not row :
        break

    if username_map.has_key(row[1]) :
        user = username_map[row[1]]
    else :
        user = row[1]

    userid_map[user] = int(row[0])
c.close()

#print userid_map

# then push it to status.net notice

for msg in local_db.iteritems() :
    c = conn.cursor()
    if not msg.replied_to :
        # insert new conversation
        c.execute('''INSERT INTO conversation (created, modified) VALUES (%s, %s)''', (msg.created, msg.created))
        conv_id = c.lastrowid
        print 'Conv ID = ', conv_id
        c.execute('''UPDATE conversation SET `uri`='%s/conversation/%d' WHERE `id`=%d''' % (BASE_STATUSNET_URL, conv_id, conv_id))
    else :
        # not yet implemented
        conv_id = None
        pass
    if conv_id :
        c.execute('''INSERT INTO notice (profile_id, content, rendered, created, modified, source, is_local, conversation) VALUES (%s, %s, %s, %s, %s, 'yammer', 1, %s)''', (userid_map[msg.owner], msg.msg, msg.msg, msg.created, msg.created, conv_id))
        notice_id = c.lastrowid
        c.execute('''UPDATE notice SET `uri`='%s/notice/%d' WHERE `id`=%d''' % (BASE_STATUSNET_URL, notice_id, notice_id))
    c.close()
    conn.commit()

