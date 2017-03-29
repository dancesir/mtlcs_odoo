#!/usr/bin/python
# -*- coding: utf-8 -*-
import _mssql
import oerplib


def Diction_Row(row):
    data = {}
    for k in row:
        if isinstance(k, (unicode, str)):
            v = row[k]
            new_k = k.lower()
            if isinstance(v, unicode):
                data[new_k] = (''.join(chr(ord(x)) for x in v)).decode('gbk')
            else:
                data[new_k] = v
    return data


def ODOO(user, passwd, dbname, server='localhost', protocol='xmlrpc', port=8069):
    odoo = oerplib.OERP(server, protocol=protocol, port=port)
    odoo.login(user, passwd, dbname)
    return odoo

def DongShuo(server, user, password, database, charset='utf8'):
    print server, user, password, database
    conn = _mssql.connect(server=server, user=user, password=password, database=database, charset=charset)
    return conn


class Connector():
    def __init__(self, arg={}):
        odoo_user = arg.get('odoo_user', 'admin')
        odoo_passwd = arg.get('odoo_passwd', 'admin')
        odoo_dbname = arg.get('odoo_dbname', 'odoo')
        odoo_server = arg.get('odoo_server', 'localhost')
        odoo_protocol = arg.get('odoo_protocol', 'xmlrpc')
        odoo_port = arg.get('odoo_port', 8069)
        dongshuo_server = arg.get('dongshuo_server','192.168.10.2')
        dongshuo_user = arg.get('dongshuo_user','sa')
        dongshuo_password = arg.get('dongshuo_password','719799')
        dongshuo_database=arg.get('dongshuo_database','mtlerp-running')


        self.arg = arg
        self.odoo = ODOO(odoo_user, odoo_passwd, odoo_dbname, odoo_server, odoo_protocol, odoo_port)
        self.dongshuo = DongShuo(dongshuo_server, dongshuo_user, dongshuo_password, dongshuo_database)

    def dongshuo_query(self, sql):
        self.dongshuo.execute_query(sql)
        return self.dongshuo

    def Diction_Row(self, row):
        data = {}
        for k in row:
            if isinstance(k, (unicode, str)):
                v = row[k]
                new_k = k.lower()
                if isinstance(v, unicode):
                    data[new_k] = (''.join(chr(ord(x)) for x in v)).decode('gbk')
                else:
                    data[new_k] = v
        return data
