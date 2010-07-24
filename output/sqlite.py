#!/usr/bin/python

import types
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, Unicode, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import and_, or_, not_, func, select

from base import Output, Message

metadata = MetaData()

message = Table('messages', metadata,
        Column('id', Integer, primary_key = True),
        Column('yammer_id', Integer, unique = True, nullable = False, index = True),
        Column('owner', String(100), nullable = False, index = True),
        Column('msg', Unicode, nullable = False, index = True),
        Column('created', DateTime, nullable = False, index = True),
        Column('replied_to', Integer, default = None, index = True),
        Column('client', String(128), default = 'web'),
        Column('migrated_id', Integer, default = None)
    )

mapper(Message, message)

class SqliteOutput(Output) :
    def __init__(self, yammer, url, **kw) :
        Output.__init__(self, yammer, url, **kw)
        self.url = url
        #print 'Got URL: ', self.url
        self.engine = create_engine(self.url, echo=True, convert_unicode = True)
        metadata.create_all(self.engine)
        self.conn = self.engine.connect()
        self.session = sessionmaker(bind = self.engine)()

    def commit(self) :
        if self.session :
            self.session.commit()
        
    def put(self, msg) :
        created = datetime.strptime(msg['created_at'], '%Y/%m/%d %H:%M:%S +0000')
        #print created
        #print msg['created_at']
        owner = self.get_user(int(msg['sender_id']))
        replied_to_id = msg['replied_to_id'] or None
#        print 'Owner = ', owner
        val = {'yammer_id' : msg['id'], 'owner': owner, 'msg' : msg['body']['plain'],
                'created':created, 'replied_to':replied_to_id, 'client':msg['client_type']}
        #print val
        #self.conn.execute(message.insert(values=val))
        #print self.session
        self.session.add(Message(**val))

    def get_min_id(self) :
        rows = self.conn.execute(select([func.min(message.c.yammer_id)]))
        result = rows.fetchone()
        if result :
            return result[0]
        else :
            return None

    def iteritems(self) :
        for item in self.session.query(Message).order_by(Message.created) :
            yield item

output = SqliteOutput
