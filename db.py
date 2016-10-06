"""
* 
* db.py
* Author:
* Renato Jensen Filho
* 2016-10-06
* 
"""

import psycopg2
from urllib.parse import urlparse, uses_netloc

uses_netloc.append("postgres")
  
class Database:
   
   #constructor
   def __init__(self, db_url):      
      self.url = urlparse(db_url)
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)
      self.cur=self.conn.cursor()
      self.cur.execute("CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, url TEXT, stats TEXT)")
      self.conn.commit()
      self.conn.close()
   
   #inserts a new image in images table. If there are more than 10 rows, deletes older rows until there are only 9 rows left (then inserts the 10th row)   
   def insert(self, url, stats):
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)      
      self.cur=self.conn.cursor()
      self.cur.execute("INSERT INTO images(url,stats) SELECT %s, %s WHERE NOT EXISTS (SELECT url FROM images WHERE url=%s)", (url, stats, url))
      self.cur.execute("SELECT COUNT(*) OVER (), i.id FROM images i")
      row=self.cur.fetchone()
      i = int(row[0]) 
      if i > 10:
         self.cur.execute("DELETE FROM images WHERE id = any (array(SELECT id FROM images ORDER BY id LIMIT %s))", (i-10,))
      self.conn.commit()
      self.conn.close()
   
   #selects the last 10 rows
   def view(self):
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)
      self.cur=self.conn.cursor()
      self.cur.execute("SELECT * FROM images ORDER BY id DESC LIMIT 10")
      rows=self.cur.fetchall()
      self.conn.close()
      return rows

   def delete(self, id):
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)
      self.cur=self.conn.cursor()
      self.cur.execute("DELETE FROM images WHERE id=%s", (id,))
      self.conn.commit()
      self.conn.close()

   def update(self, id, url="", stats=""):
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)
      self.cur=self.conn.cursor()
      self.cur.execute("UPDATE images SET url=%s, stats=%s WHERE id=%s", (url,stats,id))
      self.conn.commit()
      self.conn.close()

   #destructor
   def __del__(self):
      if self.conn.closed == 0:
         self.conn.close()