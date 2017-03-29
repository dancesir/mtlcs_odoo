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
from openerp import SUPERUSER_ID


class production_plan_month(osv.osv):
    _name = 'production.plan.month'
    _order = 'id desc'

    def _compute_name(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = '[%s] %s' % (p.month_id.name, p.value)
        return res

    _columns = {
        'name': fields.function(_compute_name, type='char', size=64, string=u'月计划', store=True, readonly=True),
        'state': fields.selection([('draft', u'草稿'), ('wait_plan', u'待计划'), ('done', u'完成')], u'状态'),
        'month_id': fields.many2one('year.month', u'年月', ondelete='restrict', readonly=True,
                                    states={'draft': [('readonly', False)]}),
        'value': fields.float(u'有效：平方米', states={'done': [('readonly', True)]}),
        'count_layer' : fields.float(u'平均层数', readonly=True, states={'draft': [('readonly', False)]}),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'note': fields.text(u'备注', readonly=True, states={'draft': [('readonly', False)]}),

        # ==========multi company0117
        # 'company_id': fields.many2one('res.company', readonly=True,  string=u'公司'),
    }

    _defaults = {
        'state': 'draft',
        'month_id': lambda self, cr, uid, ctx: self._default_month(cr, uid, context=ctx),
        'count_layer': 4,
        # ==========multi company0117
        # 'company_id': lambda self, cr, uid, ctx:self._default_company(cr, uid, context=ctx),
    }

    # ==========multi company0118
    # def _default_company(self, cr, uid, context=None):
    #     company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
    #     return company_id or None

    def _default_month(self, cr, uid, context=None):
        month_obj = self.pool.get('year.month')
        month_ids = month_obj.search(cr, uid, [('name','=',time.strftime('%Y-%m'))], limit=1)
        return month_ids and month_ids[0] or None

    _sql_constraints = [
        # ==========multi company0118
        # ('month_uniq', 'unique(month_id, company_id)', u'同一公司月生产计划的年月不能重复'),
        ('month_uniq', 'unique(month_id)', u'月生产计划的年月不能重复'),
    ]

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'wait_plan'}, context=context)
        return True

    def plan_approve(self, cr, uid, ids, context=None):
        for ppm in self.browse(cr, uid, ids, context=context):
            if ppm.value <=0:
                raise osv.except_osv(_('Error!'),  (u'平米数不能小于0'))
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        for data in self.read(cr, uid, ids, ['state']):
            if data['state'] != 'draft':
                raise osv.except_osv(_('Error'), _( u"非草稿状态不可删除"))

        return super(production_plan_month, self).unlink(cr, uid, ids, context=context)
    

        # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
