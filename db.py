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
   def __init__(self, url):      
      url = urlparse(url)
      self.conn=psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
      self.cur=self.conn.cursor()
      self.cur.execute("CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, url TEXT, stats TEXT)")
      self.conn.commit()
   
   #inserts a new image in images table. If there are more than 10 rows, deletes older rows until there are only 9 rows left (then inserts the 10th row)   
   def insert(self, title, author, year, isbn):
      self.cur.execute("SELECT COUNT(*) OVER (), i.id FROM images i")
      row=self.cur.fetchone()
      if int(row['count']) >= 10:
         self.cur.execute("DELETE FROM images WHERE id = any (array(SELECT id FROM images ORDER BY id LIMIT %s))", (int(row['COUNT'])-9))
      
      self.cur.execute("INSERT INTO images(url,stats) VALUES(%s,%s)", (url, stats))
      self.conn.commit()
   
   #selects the last 10 rows
   def view(self):
      self.cur.execute("SELECT * FROM images ORDER BY id DESC LIMIT 10")
      rows=self.cur.fetchall()
      return rows

   def delete(self, id):
      self.cur.execute("DELETE FROM images WHERE id=%s", (id,))
      self.conn.commit()

   def update(self, id,title="", author="", year="", isbn=""):
      self.cur.execute("UPDATE images SET url=%s, stats=%s WHERE id=%s", (url,stats,id))
      self.conn.commit()

   #destructor
   def __del__(self):
      self.conn.close()