# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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

from openerp.osv import osv, fields

class hr_department(osv.osv):
    _inherit = 'hr.department'
    _order = 'ref'

    def _compute_complete_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for d in self.browse(cr, uid, ids, context=context):
            code = d.ref or None
            parent_complete_code = d.parent_id and d.parent_id.complete_code
            if parent_complete_code and code:
                code = '%s.%s' % (parent_complete_code, code)
            res[d.id] = code
        return res

    _columns = {
        'ref': fields.char(u'部门代码', size=20),
        'complete_code': fields.function(_compute_complete_code, string=u'完整编码', type='char', size=40, store=True, readonly=True),
        # ==========multi company
        # 'company_id': fields.many2one('res.company', readonly=True, string=u'公司'),
    }
    _defaults = {
        # ==========multi company
        # 'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    }
    _sql_constraints = [
        # ==========multi company
        # ('code_ref', 'unique (ref, company_id)', u'部门代码不能重复'),
        ('code_ref', 'unique (ref)', u'部门代码不能重复'),
    ]


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'code': fields.char(u'工号', size=16, required=True),
    }

    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'工号不能重复'),
    ]
