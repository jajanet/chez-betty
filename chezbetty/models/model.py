import datetime
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Float,
    Text,
    Enum,
    DateTime,
    ForeignKey,
    Boolean
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    validates,
    relationship,
    object_session,
    )

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql.expression import or_
from zope.sqlalchemy import ZopeTransactionExtension

from .history_meta import Versioned, versioned_session

from pyramid.security import Allow, Everyone

DBSession = versioned_session(scoped_session(sessionmaker(extension=ZopeTransactionExtension())))
Base = declarative_base()

class RootFactory(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, 'user', 'user'),
        (Allow, 'serviceaccount', 'service'),
        (Allow, 'manager', 'manage'),
        (Allow, 'admin', 'admin'),
    ]

    def __init__(self, request):
        pass

