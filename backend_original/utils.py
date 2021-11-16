# -*- coding: UTF-8 -*-
'''
Description  : 
Author       : zyl
Date         : 2021-10-26 21:50:13
LastEditTime : 2021-11-08 10:23:22
FilePath     : \\splicetools\\backend_original\\utils.py
'''
import logging
import pathlib
import json
import time
import sqlite3



class Results:
    def __init__(self):
        self.code = 200
        self.msg = 'ok'

    def ok(self, data):
        self.code = 200
        self.msg = 'ok'
        self.data = data
        return json.dumps(self.__dict__)

    def err(self, msg='error'):
        self.code = 500
        self.msg = msg
        return json.dumps(self.__dict__)


def log(message, level=logging.INFO):
    (pathlib.Path(__file__)/'../log/').mkdir(exist_ok=True)
    logging.basicConfig(filename=pathlib.Path(__file__) / "../log/{0}.log".format(time.strftime("%Y-%m-%d", time.localtime())),
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%m-%d_%H:%M:%S',
                        level=logging.INFO)

    logging.log(level, message)


def getConfig(column='*'):
    db = Database('app')
    return db.getLast('config',  column)


class Database:
    def __init__(self, name=None):
        self.conn = None
        self.cursor = None
        if name:
            self.open(name)

    def open(self, name):
        try:
            self.conn = sqlite3.connect(pathlib.Path(
                __file__) / "../{0}.db".format(name))
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print("Error connecting to database!")

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get(self, table, columns, limit=None):
        query = "SELECT {0} from {1};".format(columns, table)
        self.cursor.execute(query)
        # fetch data
        rows = self.cursor.fetchall()
        text = {}
        data = []
        for row in rows:
            for s, x in enumerate(self.cursor.description):
                text[x[0]] = row[s]
            data.append(text)
        return data[len(data) - limit if limit else 0:]

    def getLast(self, table, columns):
        return self.get(table, columns, limit=1)[0]

    def write(self, table, columns, data):
        sql = "INSERT INTO {0} ({1}) VALUES ('{2}');".format(
            table, columns, data)
        log(sql)
        self.cursor.execute(sql)
        self.close()

    def query(self, sql):
        log(sql)
        self.cursor.execute(sql)
        self.close()


def dbLog(projectId, key, value):

    db = Database('app')
    if projectId == 'insert':
        db.write('log', 'projectId', value)
    else:
        column = "{0}='{1}'".format(key, value)
        db.query("update log set {0} where projectId='{1}'".format(
            column, projectId))
