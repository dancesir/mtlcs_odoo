# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
import pymssql
import logging
from openerp.exceptions import Warning
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

_logger = logging.getLogger(__name__)

class MSSQL(object):
    def __init__(self,  server='', user='', password='', database=''):
        self.con = pymssql.connect(server=server, user=user, password=password, database=database,)
        self.cr = self.con.cursor()

    def get_max_SN(self, tbname):
        self.cr.execute('select isnull(max(SN),0) as SN from %s' % tbname)
        return self.cr.fetchall()[0][0]

    def exec_non_query(self):
        self.con.commit()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _description = "Attendance"

    _columns = {
        'name': fields.datetime('Date', required=True, select=1, readonly=True),
        'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action',),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, select=True, readonly=True),
        'code': fields.related('employee_id', 'code', type='char', relation='hr.employee', string=u'工号',readonly=True),
        'DF_SN':fields.integer(string=u'DF编号', readonly=True),
    }

    _defaults = {
        # 'name': lambda *a: datetime.utcnow().strftime(DTF),
        # 'action': 'sign_in',
    }

    def _altern_si_so(self, cr, uid, ids, context=None):
        return super(hr_attendance, self)._altern_si_so(self, cr, uid, ids, context=None)

    _constraints = [
        (_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', [''])]

    def format_values(self, cr, uid, ids, values, local_max_SN, context=None):
        datas = []
        codes = []
        employee_ids = []
        employee_dic = {}

        # 取得所有职员的code, id
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [])
        for employee in self.pool.get('hr.employee').browse(cr, uid, employee_ids):
            # codes.append(employee.code)
            # employee_ids.append(employee.id)
            employee_dic.update({employee.code: employee.id})

        i = 0
        for value in values:
            # value[0]:DF_SN, value[1]:职员编号, value[2]:考勤日期, value[3]:考勤时间,
            code = '%s%s'%('cs',value[1])
            if code in employee_dic.keys() and value[0] > local_max_SN:
                str_time = '%s%s%s'%(value[2].strftime('%Y-%m-%d'), ' ', value[3])
                # time_array = datetime.strptime(str_time, DTF)
                time_struct = time.mktime(datetime.strptime(str_time, DTF).timetuple())

                data = {
                    'employee_id': employee_dic.get(code),
                    'name': datetime.utcfromtimestamp(time_struct).strftime(DTF),
                    'DF_SN': value[0],
                    'code': '%s%s' % ('cs', value[1]),
                }

                datas.append(data)
            else:
                i += 1
                _logger.info(u'没有编号为:%s 的员工[%s]' % (value[1],i))

        return datas

    def create_attendance(self, cr, uid, datas, context=None):
        for data in datas:
            self.create(cr, uid, data, context=context)
            _logger.info(u'正在同步:%s'%(data))
        _logger.info(u'==同步完成==')
        return True

    def sync_from_DF(self, cr, uid, ids, context=None):
        # 连接服务器
        DF_CARD_config = {'server': '192.168.10.8', 'user': 'sa', 'password': '719799', 'database': 'DF_CARD', }
        DF_CARD = MSSQL(**DF_CARD_config)
        cr_run = DF_CARD.cr
        DF_max_SN = DF_CARD.get_max_SN('Att_Raw_Data')

        # 取本地最大DF_SN
        maxID = self.pool.get('hr.attendance').search(cr, uid, args=[('DF_SN', '!=', '')], offset=0, limit=1, order='DF_SN DESC')
        local_max_SN = self.browse(cr, uid, maxID, context=context).DF_SN and self.browse(cr, uid, maxID, context=context).DF_SN or 0

        if DF_max_SN == local_max_SN:
            DF_CARD.exec_non_query()
            raise Warning(u'已经是最新数据，无须再同步')

        # 从服务器读取需要同步数据
        # str_where = 'where datediff(day,RDate,getdate())<= 2 and datediff(day,RDate,getdate())>= 0'
        # str_where = 'where SN>%s' % (local_max_SN)
        str_where = "where SN>%s and RDate>='2017-01-01'" % (local_max_SN)
        query = 'select top %s SN, PersonnelID, RDate, RTime from %s %s order by SN ASC' % ('10000','Att_Raw_Data', str_where)
        cr_run.execute(query)
        values = cr_run.fetchall()

        # 服务器数据处理
        datas = self.format_values(cr, uid, ids, values, local_max_SN, context=None)

        # 处理后数据写入本地数据库
        self.create_attendance(cr, uid, datas, context=context)

        DF_CARD.exec_non_query()

        return True



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
