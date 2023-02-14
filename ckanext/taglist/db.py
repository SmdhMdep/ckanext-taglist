import datetime
import ckan.model as model

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types
from ckan.model.meta import metadata,  mapper, Session
from ckan.model.types import make_uuid

#Schema of centraltags table
#important columns:
#tagname = holds the name of the tag to be added
#Added = false(not yet added) true(added to tags)
centraltags_table = Table('centraltags', metadata,
    Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
    Column('tagname', types.UnicodeText),
    Column('user_id', types.UnicodeText, default=u''),
    Column('created_at', types.DateTime, default=datetime.datetime.utcnow),
    Column('Added', types.BOOLEAN, default=False)
)

#Commands that can be preformed on table
class centraltags(model.DomainObject):
    # Allows for data to be queried 
    def __getitem__(self, field):
        return self.__dict__[field]
        
    @classmethod
    def get(cls, **kw):
        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    @classmethod
    def find(cls, **kw):
        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(**kw)

    #Updates Added column
    @classmethod
    def updateAdded(cls, isAdded, **kw):
        query = model.Session.query(cls).autoflush(False)
        user = query.filter_by(**kw).first()
        user.Added = isAdded
        model.Session.commit()
        return True

model.meta.mapper(centraltags, centraltags_table)