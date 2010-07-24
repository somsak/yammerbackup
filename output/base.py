import sys

class Output(object) :
    def __init__(self, yammer, url, **kw) :
        self.yammer = yammer
        self.user_dict = {}

    def commit(self) :
        pass

    def put(self, msg) :
        pass

    def get_user(self, id) :
        try :
            return self.user_dict[id]
        except KeyError :
            # fetch from yammer instead
            user_info = self.yammer.get_user_info(id)
            print user_info['name']
            #sys.exit(1)
            self.user_dict[id] = user_info['name']
            return self.user_dict[id]

    def get_min_id(self) :
        pass

class Message(object) :
    def __init__(self, **kw) :
        self.id = kw.get('id', None)
        self.yammer_id = kw.get('yammer_id', None)
        self.owner = kw.get('owner', None)
        self.msg = unicode(kw.get('msg', ''))
        self.created = kw.get('created', None)
        self.replied_to = kw.get('replied_to', None)
        self.client = kw.get('client', '')
        self.migrated_id = kw.get('migrated_id', None)

    def __repr__(self) :
        return '<Message(%d, %s)>' % (self.id, self.owner)


