#!/usr/bin/python

import types
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, ForeignKey   
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import and_, or_, not_, func, select

metadata = MetaData()

message = Table('messages', metadata,
        Column('id', Integer, primary_key = True),
        Column('yammer_id', Integer, unique = True, nullable = False, index = True),
        Column('msg', String(300), nullable = False, index = True),
        Column('created', DateTime, nullable = False, index = True),
        Column('replied_to', Integer, default = None, index = True),
        Column('client', String(128), default = 'web')
    )

class Message(object) :
    def __init__(self, **kw) :
        self.id = kw.get('id', None)
        self.yammer_id = kw.get('yammer_id', None)
        self.msg = unicode(kw.get('msg', ''))
        self.created = kw.get('created', None)
        self.replied_to = kw.get('replied_to', None)
        self.client = kw.get('client', '')

    def __repr__(self) :
        return '<Message(%d, %s)>' % (self.id, self.msg)

mapper(Message, message)

class SqliteOutput(object) :
    def __init__(self, url, **kw) :
        self.url = url
        #print 'Got URL: ', self.url
        self.engine = create_engine(self.url, echo=True)
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
        replied_to_id = msg['replied_to_id'] or None
        val = {'yammer_id' : msg['id'], 'msg' : msg['body']['plain'],
                'created':created, 'replied_to':replied_to_id, 'client':msg['client_type']}
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

output = SqliteOutput
