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
from openerp.osv import fields, osv


class res_users(osv.osv):
    _inherit = "res.users"

    def _get_department(self, cr, uid, ids, fieldname=None, arg=None, context=None):
        res = {}
        for u in self.browse(cr, uid, ids, context=context):
            res[u.id] = u.employee_ids and u.employee_ids[0].department_id.id or False
        return res

    _columns = {
        'default_department_id': fields.function(_get_department, type='many2one', relation='hr.department', readonly=True, string=u'部门'),
        # 'company_ids': fields.many2many('res.company', 'res_company_ref', 'user_id', 'company_id', string=u'公司'),

    }
    _defaults = {
        'lang': 'zh_CN',
    }

    def create(self, cr, uid, values, context=None):
        if not values.get('email'):
            values.update({'email': 'none@none.com'})
        return super(res_users, self).create(cr, uid, values, context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
