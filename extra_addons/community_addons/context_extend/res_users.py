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
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.exceptions import except_orm, Warning, RedirectWarning

# class res_users(osv.osv):
#     _inherit = 'res.users'
#
#     # 获取用户关联的部门
#     def _get_self_department_ids(self, cr, uid, ids, name, args, context=None):
#         result = dict.fromkeys(ids, False)
#         emp = self.pool.get('hr.employee')
#         for id in ids:
#             emp_ids = emp.search(cr, uid, [('user_id', '=', id)], context=context)
#             emp = emp.browse(cr, uid, emp_ids[0], context=context)
#             result[id] = emp.department_id
#         return result
#
#     _columns = {
#         'context_department_id': fields.function(_get_self_department_ids, type="many2one", relation="hr.department", string="Context Department"),
#     }


