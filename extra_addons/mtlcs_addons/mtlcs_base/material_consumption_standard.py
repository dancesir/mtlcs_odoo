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


class material_consumption_standard(osv.osv):
    _name = 'material.consumption.standard'

    def _compute_name(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for s in self.browse(cr, uid, ids, context):
            res[s.id] = '[%s]-%s' % (s.product_id.default_code, s.department_id.name)
        return res

    def _compute_value(self, cr, uid, ids, field_name, arg=None, context=None):
        uom_obj = self.pool.get('product.uom')

        res = {}
        for s in self.browse(cr, uid, ids, context=context):
            if s.uom_id.id == s.unit_id.id:
                res[s.id] = s.uom_value
            else:
                res[s.id] = uom_obj._compute_qty(cr, uid, s.uom_id.id, s.uom_value, s.unit_id.id, round=False, rounding_method='UP')
        return res

    _columns = {
        'name': fields.function(_compute_name, type="char", string=u"标准", readonly=True,
                                store={'material.consumption.standard': (
                                    lambda self, cr, uid, ids, c={}: ids, ['product_id', 'department_id'], 50)}),
        'product_id': fields.many2one('product.product', u'物料', required=True, readonly=True,
                                      states={'draft': [('readonly', False)], }, ),
        'department_id': fields.many2one('hr.department', u'部门', required=True, readonly=True,
                                         states={'draft': [('readonly', False)], }, ),
        'value': fields.float(u'标准值', digits=(4,4),  required=True, readonly=True, states={'draft': [('readonly', False)], }, ),

        #'value': fields.function(_compute_value, type='float', store=True, string='基准单位用量'),
        'unit_id': fields.related('product_id', 'uom_id', type="many2one", relation="product.uom", readonly=True,string=u"基准单位"),
        #'unit_categ_id': fields.related('unit_id', 'category_id', type='many2one', relation='product.uom.categ', readonly=True, string=u'单位分类'),
        #'uom_value': fields.float(u'标准值', digits=(4,4),),
        #'uom_id': fields.many2one('product.uom', u'标准值单位'),

        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'create_date': fields.datetime(u'创建时间', readonly=True),
        'end_date': fields.datetime(u'作废时间', readonly=True),
        'type': fields.selection([('area', u'根据计划生产面积'), ('period',u'根据历史采购数据'),('employee_count',u'基于部门职员数'),('fixed',u'固定用量')], u'类型', readonly=True,
                                 states={'draft': [('readonly', False)], }, ),
        'state': fields.selection([('draft', u'草稿'), ('w_general_manager', u'待总经理'),('normal', u'生效'), ('abolish', u'作废')], u'状态'),
        'state_update': fields.selection([('draft', u'草稿'),('w_general_manager', u'待总经理'),('done', u'完成'), ], u'修改状态'),
        'new_value': fields.float(u'新标准值', readonly=True, states={'normal': [('readonly', False)], }, ),
        'reason': fields.char(u'标准修改原因', size=64),
        # 'active': fields.boolean(u'有效'),
        'standard_id': fields.many2one('material.consumption.standard', u'历史记录', readonly=True),

        # ==========multi company
        # 'company_id': fields.many2one('res.company', readonly=True, string=u'公司'),

    }

    _defaults = {
        'state': 'draft',
        'state_update':'draft',
        #'active': True,
        'type': 'area',
        # ==========multi company
        # 'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    }

    def _check_unic(self, cr, uid, ids, context=None):
        for mcs in self.browse(cr, uid, ids, context=context):
            domain = [('product_id', '=', mcs.product_id.id), ('department_id', '=', mcs.department_id.id),
                      ('state', '=', 'normal'), ('id', '!=', mcs.id)]
            res = self.search(cr, uid, domain, limit=1)
            if res:
                return False
        return True

    _constraints = [
        (_check_unic, u'物料和部门不可以重复', ['product_id', 'department_id', 'state']),
    ]

    def get_need_qty(self, cr, uid, ids, area=0.0, standards=None, context=None):
        move_obj = self.pool.get("stock.move")
        uom_obj = self.pool.get("product.uom")
        standards = standards or self.browse(cr, uid, ids, context=context)

        cr.execute("SELECT product_id, product_min_qty FROM stock_warehouse_orderpoint WHERE active = 't'")
        res = cr.fetchall()
        point_dict = dict(res)

        res = {}
        for std in standards:
            plan_qty = 0
            if std.type == 'area':
                location_qty = std.product_id.qty_available
                saft_qty = point_dict.get(std.product_id.id, 0.0)
                plan_qty = (area * std.value) + saft_qty - location_qty + (0 * 0)  #TODO get 0*0
            elif std.type == 'fixed':
                plan_qty = std.value
            elif std.type == 'employee_count':
                pass
                #TODO
                #plan_qty
            res[std.id] = plan_qty

        return  res

    def confirm(self, cr, uid, ids, context=None,):
        for s in self.browse(cr, uid, ids, context=context):
            if s.value <=0:
                raise osv.except_osv(_('Error'), _(u"标准值不能小于0") )
            self.write(cr, uid, s.id, {'state': 'w_general_manager'}, context=context)
        return True

    def general_manager_approve(self, cr, uid, ids, context=None,):
        self.write(cr, uid, ids, {'state': 'normal'}, context=context)
        return True

    def request_update(self, cr, uid, ids, context=None):
        for s in self.browse(cr, uid, ids, context=context):
            if s.new_value <=0:
                raise osv.except_osv(_('Error'), _( u"新标准值不能小于0") )
            self.write(cr, uid, s.id, {'state_update': 'w_general_manager'}, context=context)
        return True

    def general_manager_approve_update(self, cr, uid, ids, context=None):
        return self.update_standard(cr, uid, ids, context=context)

    def update_standard(self, cr, uid, ids, context=None):
        standard = self.browse(cr, uid, ids[0], context=context)
        #abolish this record
        self.write(cr, uid, standard.id, {'state': 'abolish', 'state_update':'done'}, context=context)
        #create a new record
        default = {
            'state': 'normal',
            'state_update': 'draft',
            'uom_value': standard.new_value,
            'new_value': 0,
            'standard_id':standard.id,
            'reason':None,
        }
        new_id = self.copy(cr, uid, standard.id, default=default, context=context)
        return {
            'name': _(u'新标准'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'material.consumption.standard',
            'res_id': new_id,
            'type': 'ir.actions.act_window',
        }

    def get_normal_ids(self, cr, uid, context=None):
        normal_ids = self.search(cr, uid, [('state', '=', 'normal')], context=context)
        return normal_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
