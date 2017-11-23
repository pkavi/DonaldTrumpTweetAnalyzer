#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
import pandas as pd
import psycopg2
#https://www.trackalytics.com/twitter/profile/realDonaldTrump/

r=open('Donald J. Trump _ Twitter Statistics _ Analytics _ Trackalytics.html').read()
followersPage = BeautifulSoup(r,"html.parser")
table=followersPage.findAll(lambda tag: tag.name=='table')
if len(table)!=1:
    print("error")
table=table[0]
rows=table.findAll(lambda tag: tag.name=='tr')


conn = psycopg2.connect("dbname=TweetsDatabase user=pkavikon")
cur = conn.cursor()



print(len(rows))
rejectedRows=0
for row in rows:
    cells=row.findAll(lambda tag: tag.name=='td')
    if len(cells)==0:
        rejectedRows+=1
        continue
    followers=int(cells[2].text.encode('utf8').split(" ")[0].replace(",",""))
    dateFollowers=pd.to_datetime(cells[1].text.encode('utf8').replace(",","").strip(), format='%B %d %Y')
    cur.execute("select date from followersTable where date=%s;",(dateFollowers.strftime("%Y-%m-%d").encode('utf8'),))
    if cur.fetchone() is not None:
        print("delete and reinsert: "+ str(dateFollowers.strftime("%Y-%m-%d")))
        cur.execute("DELETE FROM followersTable WHERE date=%s;",(dateFollowers.strftime("%Y-%m-%d").encode('utf8'),))
    cur.execute("INSERT INTO followersTable (date,followers) VALUES (%s,%s);",(dateFollowers.strftime("%Y-%m-%d").encode('utf8'),followers))
    conn.commit()

print(rejectedRows)

cur.close()
conn.close()

    





