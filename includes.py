from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

Base = declarative_base()

class User(Base):
  __tablename__ = "users"

  uid = Column(Integer, primary_key=True)
  name = Column(String)
  nick = Column(String)

  def __init__(self, uid, name, nick):
    self.uid = uid
    self.name = name
    self.nick = nick

  def __repr__(self):
    return "<User(uid='%s', name='%s', nick='%s')>" % (self.uid, self.name, self.nick)


class Event(Base):
  __tablename__ = "events"

  eid = Column(Integer, primary_key=True)
  name = Column(String)
  archive = Column(Boolean)

  def __init__(self, eid, name, archive=False):
    self.eid = eid
    self.name = name
    self.archive = archive

  def __str__(self):
    return "%s - Event %s" % (self.eid, self.name)

  def __repr__(self):
    return "<Event(eid='%s', name='%s', archive='%s')" % (self.eid, self.name, self.archive)


class Order(Base):
  __tablename__ = "orders"

  eid = Column(Integer, ForeignKey('events.eid'), primary_key=True)
  uid = Column(Integer, ForeignKey('users.uid'), primary_key=True)
  data = Column(String)

  def __init__(self, eid, uid, data):
    self.eid = eid
    self.uid = uid
    self.data = data

  def __str__(self):
    return "%s - %s - Order %d" % (self.eid, self.oid, self.data)

  def __repr__(self):
    return "<Order(eid='%s', uid='%s', data='%s')" % (self.eid, self.uid, self.data)
