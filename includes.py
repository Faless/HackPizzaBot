

class User:
  def __init__(self, uid, name, nick):
    self.uid = uid
    self.name = name
    self.nick = nick


class Event:

  def __init__(self, eid, name, archive=False):
    self.eid = eid
    self.name = name
    self.archive = archive

  def __str__(self):
    return "%s - Event %s" % (self.eid, self.name)


class Order:

  def __init__(self, eid, uid, data):
    self.eid = eid
    self.uid = uid
    self.data = data

  def __str__(self):
    return "%s - %s - Order %d" % (self.eid, self.oid, self.data)
