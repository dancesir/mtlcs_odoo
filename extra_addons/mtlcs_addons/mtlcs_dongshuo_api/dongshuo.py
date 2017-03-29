#!/usr/bin/python
# -*- coding: utf-8 -*-
import _mssql


class Dongshuo(object):
    def __init__(self,server, user, password, database, charset='utf8'):
        self.conn = _mssql.connect(server=server, user=user, password=password, database=database, charset=charset)


conn1 = Dongshuo('192.168.10.2', 'sa', '719799', 'mtlerp-running')
print conn1















