#!/usr/bin/env python

import json
import sqlite3
import uuid

path  = '/home/django/djangoprojects/testtest/regions.json'
pathC = '/home/django/djangoprojects/testtest/city.json'

conn = sqlite3.connect("/home/django/djangoprojects/db.sqlite3")  # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

print(path)

with open(path, 'r', encoding='utf-8') as f:

    text = json.loads(f.read())

    for e in text['items']:

        cur = conn.cursor()
        cur.execute("SELECT * FROM main_region WHERE name=?", (e['name'],))

        rows = cur.fetchall()

        if len(rows) == 0:

            hhh = "INSERT INTO main_region VALUES('"+str(uuid.uuid4()).replace('-', '')+"','"+e['name']+"', '00000000000000000000000000000000')"

            #print(hhh)
            cursor.execute(hhh)
            # Сохраняем изменения
            conn.commit()
    #cursor.execute(
    #    "INSERT INTO main_country VALUES('00000000000000000000000000000000', 'Неопределено', '')")
    # Сохраняем изменения
    #conn.commit()


with open(pathC, 'r', encoding='utf-8') as f:

    text = json.loads(f.read())

    for e in text['items']:

        cur = conn.cursor()
        cur.execute("SELECT * FROM main_city WHERE name=?", (e['name'],))

        rows = cur.fetchall()

        if len(rows) == 0:

            cur = conn.cursor()
            cur.execute("SELECT * FROM main_region WHERE name=?", (e['region'],))

            rows = cur.fetchall()

            if len(rows) == 0:

                region = '00000000000000000000000000000000'

            else:

                region = rows[0][0]


            hhh = "INSERT INTO main_city VALUES('"+str(uuid.uuid4()).replace('-', '')+"','"+e['name']+"','"+e['name'].upper()+"','00000000000000000000000000000000', '"+region+"')"


            cursor.execute(hhh)
            # Сохраняем изменения
            conn.commit()
            print(hhh)
