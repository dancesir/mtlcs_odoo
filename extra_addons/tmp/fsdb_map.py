# #map a file system to db
# import psycopg2
# import os
# import cmd
# import FileSystemWatcher
#
# def callback(action, content):
#     print 'action', action
#     print 'conten', content
#
#
# fsw = FileSystemWatcher("somedir")
# fsw.NotifyFilter = FileSystemWatcher.NotifyFilters.FileName
# fsw.Created += your_callback
# fsw.EnableRaisingEvents = True
#
#
# class FSDB_MAP(object):
#
#     def __init__(self, host='127.0.0.1', path='/', port=None, passwd=None):
#         self.host = host
#         self.path = path
#         self.port= port
#         self.passwd = passwd
#
#     def
#
#
# lambd