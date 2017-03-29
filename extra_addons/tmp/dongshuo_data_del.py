import pymssql
import _mssql
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='line:%(lineno)d--->%(message)s',)


class MSSQL(object):
    def __init__(self,  server='', user='', password='', database=''):
        self.con = pymssql.connect(server=server, user=user, password=password, database=database,)
        self.cr = self.con.cursor()

    def get_trigger________________(self, top=1):
        sql = "select top %s name from sysobjects where xtype='TR';" % top
        logging.warning(sql)
        cr = self.cr
        cr.execute(sql)
        return [x[0] for x in cr.fetchall()]

    def get_count(self,tbname):
        self.cr.execute('select count(*) from %s' % tbname)
        return self.cr.fetchone[0]
        
    def del_trigger____________________(self, tigger_list=None, top=1):
        if tigger_list is None:
            tigger_list = self.get_trigger(top=top)
        cr = self.cr
        for tigger in tigger_list:
            cr.execute("drop trigger %s" % tigger)
            print 'tigger %s del ok ' % tigger
        self.con.commit()
        return True
     
    def del_row___________________(self, tbname, step=1000,  where=None, count=None):
        cr = self.cr
        sql = 'del top(%s) %s;'
        count = count or self.get_count(tbname)
        while count <=0:
            cr.execute(sql % step)
            self.con.commit()
            count -= step
            
    def get_db_struck(self):
        res = {} # {'dbname': ['col_name', col_name], }
        cr = self.cr
        cr.execute('''
select
    a.name tablename, b.name colName
from sysobjects a
    inner join syscolumns b on a.id=b.id and a.xtype='U'
    inner join systypes c on b.xtype=c.xusertype
where a.xtype='U' 
''')
        col_info = cr.fetchall()
        for (tbname, colname) in col_info: 
            #print tbname, colname
            if tbname not in res:
                cr.execute('sp_pkeys %s' % tbname)
                pkinfo = cr.fetchone()
                res[tbname] = {
                    'cols':[],
                    'pk':pkinfo and pkinfo[3] or None
                 }
            res[tbname]['cols'].append(colname)
            if colname.lower() == 'id' and res[tbname]['pk']:
                res[tbname]['pk'] = colname
                
        return res
        
    def truncate_table(self, tbname):
        pass
        

def copy_row(tbname, top=None, where=None, step=1,):
    running_config = {'server':'192.168.10.2', 'user':'sa', 'password':'719799', 'database':'running',}
    szback_config = {'server':'192.168.10.4', 'user':'sa', 'password':'719799', 'database':'sqlszbk',}
    running  = MSSQL(**running_config)
    szback = MSSQL(**szback_config)
    cr_run = running.cr
    cr_bak = szback.cr
    struck = szback.get_db_struck()
    
    query = 'select top %s * from %s  %s' % (top or 9999, tbname,  where or '')
    
    cr_run.execute(query)
    values = cr_run.fetchall()
   
    col_list_srt  = '(' +  ','.join(struck[tbname]['cols']) + ') '
    position = '( ' +  ','.join(['%s'] * len(struck[tbname]['cols']) ) + ' )'
    insert_sql = "INSERT INTO " + tbname + col_list_srt + ' VALUES' + position
    
    cr_bak.execute('set identity_insert %s on' % tbname)
    try:
        cr_bak.executemany(insert_sql, values)
    except Exception, e:
        print 'insert error:', e
    szback.con.commit()
    return True


if __name__ == '__main__':
    copy_row('TIGoodsStoreDrill', where='where id < 100',)    
print '__END__'






# conn = pymssql.connect(server='192.168.10.4', user='sa', password='719799', database='sqlszbk',)
# cr=conn.cursor()
# #cr.execute("drop trigger TR_IOrderM_Delete")
# cr.execute("select top 1 product_id From production2")
# my_id = cr.fetchone()
# print my_id
# cr.execute("delete  production2 where product_id = %s" % my_id )
# cr.close
# conn.commit()











