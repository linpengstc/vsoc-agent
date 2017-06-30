# -*- coding:utf-8 -*-
import pymongo


class DB(object):

    def __getattr__(self, item):
        return self.conn["VSOCA"][item]

    def __init__(self):
        self.conn = pymongo.MongoClient(connect=False)

    def __del__(self):
        self.conn.close()