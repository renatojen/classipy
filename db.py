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
   def __init__(self, db_url, db_max_rows="10", db_tbl_size="10"):            
      self.url = urlparse(db_url)
      self.max_rows = db_max_rows if db_max_rows != None else 10
      self.tbl_size = db_tbl_size if db_tbl_size != None else 10
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)
      self.cur=self.conn.cursor()
      self.cur.execute("CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, url TEXT, stats TEXT)")
      self.conn.commit()
      self.conn.close()
   
   #inserts a new row in images table. If there are more than [self.max_rows] rows, deletes older rows until there are only [self.max_rows] rows left. If [self.max_rows] == 0 insert infinite rows.
   def insert(self, image_url, stats):
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)      
      self.cur=self.conn.cursor()
      self.cur.execute("INSERT INTO images(url,stats) SELECT %s, %s WHERE NOT EXISTS (SELECT url FROM images WHERE url=%s)", (image_url, stats, image_url))
      if self.max_rows != 0:
         self.cur.execute("SELECT COUNT(*) OVER (), i.id FROM images i")
         row=self.cur.fetchone()
         i = int(row[0]) 
         if i > self.max_rows:
            self.cur.execute("DELETE FROM images WHERE id = any (array(SELECT id FROM images ORDER BY id LIMIT %s))", (i-self.max_rows,))
            
      self.conn.commit()
      self.conn.close()
   
   #selects the last [self.tbl_size] rows. If [self.tbl_size] == 0, selects all the rows.
   def view(self):
      self.conn=psycopg2.connect(database=self.url.path[1:], user=self.url.username, password=self.url.password, host=self.url.hostname, port=self.url.port)
      self.cur=self.conn.cursor()
      if self.tbl_size != 0:
         self.cur.execute("SELECT * FROM images ORDER BY id DESC LIMIT %s", (str(self.tbl_size),))
      else:
         self.cur.execute("SELECT * FROM images ORDER BY id DESC")
         
      rows=self.cur.fetchall()
      self.conn.close()
      return rows
   
   #destructor
   def __del__(self):
      #checks if connection is still open
      if self.conn.closed == 0:
         self.conn.close()
      
   #UNUSED
   """
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
   """