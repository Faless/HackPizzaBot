
from threading import Lock
from includes import Event, User, Order
import sqlite3

lock = Lock()

conn = sqlite3.connect('db/pizzas.db', check_same_thread=False)

c = conn.cursor()


def setup_db():
  lock.acquire()
  try:
    c.execute("CREATE TABLE IF NOT EXISTS users (uid integer primary key, name varchar(256), nick varchar(256));")
    c.execute("CREATE TABLE IF NOT EXISTS events (eid integer primary key, name varchar(256), archive integer);")
    c.execute("CREATE TABLE IF NOT EXISTS orders (uid integer primary key, eid integer, data varchar(256));")
  finally:
    lock.release()


def add_user(user):
  lock.acquire()
  try:
    c.execute("INSERT INTO users values (?,?,?);", (user.uid,user.name,user.nick))
  finally:
    conn.commit()
    lock.release()


def add_event(event):
  lock.acquire()
  try:
    c.execute("INSERT INTO events values (?,?,?);", (event.eid,event.name,event.archive))
  finally:
    conn.commit()
    lock.release()


def add_order(order):
  lock.acquire()
  try:
    c.execute("INSERT INTO orders values (?,?,?);", (order.uid,order.eid, order.data))
  finally:
    conn.commit()
    lock.release()


def del_order(eid, uid):
  lock.acquire()
  try:
    c.execute("DELETE FROM orders WHERE eid = ? AND uid = ?;", (eid, uid))
  finally:
    conn.commit()
    lock.release()


def archive_event(eid, archive=True):
  lock.acquire()
  try:
    c.execute("UPDATE events SET archive=? WHERE eid=?;", (1 if archive else 0, eid))
  finally:
    conn.commit()
    lock.release()


def list_events(archive=False):
  out = []
  lock.acquire()
  try:
    query = "SELECT eid, name, archive FROM events %s;" % "" if not archive else "WHERE archive > 0"
    for row in c.execute(query):
      out.append(Event(eid=row[0],name=row[1],archive=row[2]))
  finally:
    lock.release()

  return out

def list_users():
  out = []
  lock.acquire()
  try:
    for row in c.execute("SELECT uid, name, nick FROM users;"):
      out.append(User(uid=row[0],name=row[1],nick=row[2]))
  finally:
    lock.release()
  return out

def list_orders(eid):
  out = {}
  lock.acquire()
  try:
    for row in c.execute("SELECT orders.eid, orders.uid, orders.data, users.name, users.nick FROM orders JOIN users on orders.uid = users.uid WHERE orders.eid = ?;", (eid)):
      out[1] = {"user": User(uid=row[1], name=row[3], nick=row[4]), "Order": Order(eid=row[0],uid=row[1],data=[2])}
  finally:
    lock.release()
  return out

def get_event(eid):
  lock.acquire()
  try:
    row = c.execute("SELECT eid, name, archive FROM events WHERE eid = ?;", (eid)).fetchone()
    if row is None:
      return None
  finally:
    lock.release()

  return Event(eid=row[0],name=row[1],archive=row[2])

def get_user(uid):
  lock.acquire()
  try:
    row = c.execute("SELECT uid, name, nick FROM users WHERE uid = ?;", (uid)).fetchone()
    if row is None:
      return None
  finally:
    lock.release()
  return User(uid=row[0],name=row[1],nick=row[2])

def get_order(uid, eid):
  lock.acquire()
  try:
    row = c.execute("SELECT eid, uid, data FROM orders WHERE uid = ? AND eid = ?;", (uid, eid)).fetchone()
    if row is None:
      return None
  finally:
    lock.release()
  return Order(eid=row[0],uid=row[1],data=row[2])

