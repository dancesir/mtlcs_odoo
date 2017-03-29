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

from openerp.tools.translate import _
from openerp.osv import fields, osv
from datetime import datetime, timedelta
import calendar
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

Time_diff = 8
TDiff = timedelta(hours=Time_diff)

Month_Selection = [
    ('01', u'1月'), ('02', u'2月'), ('03', u'3月'), ('04', u'4月'), ('05', u'5月'), ('06', u'6月'),
    ('07', u'7月'), ('08', u'8月'), ('09', u'9月'), ('10', u'10月'), ('11', u'11月'), ('12', u'12月')
]
Monthes = [x[0] for x in Month_Selection]



class year_month(osv.osv):
    _name = 'year.month'
    _order = 'id desc'

    def _compute_name(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = '%s-%s' % (m.year, m.month)
        return res

    _columns = {
        'name': fields.function(_compute_name, type='char', size=16, string=u'年月', readonly=True, store=True),
        'year': fields.char(u'年', size=4, required=True),
        'month': fields.selection(Month_Selection, u'月', required=True),
        'start_time': fields.datetime(u'开始时间'),
        'end_time': fields.datetime(u'结束时间'),
    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Name of the year.month must be unique !'),
    ]

    def create_by_year(self, cr, uid, year=None, context=None):
        y = year or datetime.now().strftime('%Y')
        for m in Monthes:
            start_time = (datetime.strptime('%s-%s-01 00:00:00' % (y, m,), DTF) - TDiff).strftime(DTF)
            d = calendar.monthrange(int(y), int(m))[1]
            end_time = (datetime.strptime('%s-%s-%s 23:59:59' % (y, m, d), DTF) - TDiff).strftime(DTF)
            self.create(cr, uid, {
                'name': y + '-' + m,
                'year': y,
                'month': m,
                'start_time': start_time,
                'end_time': end_time,
            }, context=context)
        return True

    def get_now_month(self, cr, uid, context=None):
        name = datetime.now().strftime('%Y-%m')
        month_ids = self.search(cr, uid, [('name','=',name)], context=context, limit=1)
        return month_ids and (month_ids[0], name) or False

    def get_last_month(self, cr, uid, org_month=None, context=None):
        org_month = org_month or datetime.now().strftime('%Y-%m')
        year, month = [int(x) for x in org_month.split('-')]
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        last_name = '%s-%s' % (year, str(month).rjust(2,'0'))
        last_ids = self.search(cr, uid, [('name','=', last_name)], context=context, limit=1)
        return last_ids and (last_ids[0], last_name) or False

    def get_next_month(self, cr, uid, org_month=None, context=None):
        org_month = org_month or datetime.now().strftime('%Y-%m')
        year, month = [int(x) for x in org_month.split('-')]
        if month == 12:
            year += 1
            month = 01
        else:
            month += 1
        next_name = '%s-%s' % (year, str(month).rjust(2,'0'))
        next_ids = self.search(cr, uid, [('name','=', next_name)], context=context, limit=1)
        return next_ids and (next_ids[0], next_name) or False

    def get_relation_source(self, cr, uid, month_id, model, model_field, domain=None, context=None):
        domain += (model_field,'=',month_id)
        res_ids = self.pool.get(model).search(cr, uid, domain, context=context)
        return res_ids or False



















        # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
