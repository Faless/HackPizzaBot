from threading import Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from includes import Base, Event, User, Order

lock = Lock()

engine = create_engine('sqlite:///db/pizzas.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
    return db_session


def safe_add(obj):
  lock.acquire()
  try:
    db_session.add(obj)
    db_session.commit()
  except e:
    print(e)
  finally:
    lock.release()


def safe_update():
  lock.acquire()
  try:
    db_session.flush()
  except e:
    print(e)
  finally:
    lock.release()


def safe_delete(obj):
  lock.acquire()
  try:
    db_session.delete(obj)
    db_session.flush()
  except e:
    print(e)
  finally:
    lock.release()


def safe_find(entity, filter=None):
  lock.acquire()
  try:
    q = db_session.query(entity)
    if filter is not None:
     return q.filter_by(**filter).all()
    return q.all()
  except e:
    print(e)
  finally:
    lock.release()


def add_user(user):
  safe_add(obj)


def add_event(event):
  safe_add(event)


def add_order(order):
  safe_add(event)


def del_order(eid, uid):
  orders = safe_find(Order, {"uid": uid, "eid": eid})
  for order in orders:
    safe_delete(order)


def archive_event(eid, archive=True):
  events = safe_find(Event, {"eid": eid})
  for e in events:
    e.archive = archive
  safe_update()


def list_events(archive=False):
  return safe_find(Event, {"archive": archive})


def list_users():
  return safe_find(User)


def list_orders(eid):
  orders = safe_find(Order, {"eid": eid})
  out = {}
  for o in orders:
    out[o.uid] = {"user": safe_find(User, {"uid": o.uid}), "order": o}
  return out


def get_event(eid):
  out = safe_find(Event, {"eid": eid})
  if len(out) > 0:
    return out[0]
  return None


def get_user(uid):
  out = safe_find(User, {"uid": uid})
  if len(out) > 0:
    return out[0]
  return None


def get_order(uid, eid):
  out = safe_find(User, {"uid": uid, "eid": eid})
  if len(out) > 0:
    return out[0]
  return None


