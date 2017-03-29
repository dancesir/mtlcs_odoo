# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Jean LELIEVRE <jean.lelievre@elico-corp.com>
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
import openerp
from openerp.osv import osv, fields
from openerp.exceptions import  Warning




Quality_ref_selection = [('stock.picking', u'Picking')]
Quality_type = [('iqc','IQC')]


Inspection_State = [
    ('draft', u'草稿'),
    ('w_quality_manager',u'待经理'),
    ('w_purchase', u'待采购主管'),
    #('w_production_chief_inspector', u'待制造总监'),
    ('w_make_return', u'待退货/退款'),
    ('done', u'完成')
]

class quality_inspection_order(osv.osv):
    # ========1121
    _inherit = ['mail.thread', 'approve.log.thread']
    _name = 'quality.inspection.order'
    _approve_log = ['state']

    _columns = {
        'name': fields.char(u'质检单', size=16, readonly=True, states={'draft': [('readonly', False),]}),
        'partner_id': fields.many2one('res.partner', u'供应商', readonly=True, states={'draft': [('readonly', False),]}),
        'type': fields.selection(Quality_type, u'类型', required=True, readonly=True, states={'draft': [('readonly', False),]}),
        'state': fields.selection(Inspection_State, u'状态'),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'user_id': fields.many2one('res.users', u'质检人', readonly=True),
        'create_date': fields.datetime(u'日期', readonly=True),
        'origin': fields.char(u'源', size=32, readonly=True, states={'draft': [('readonly', False),]}),
        'note': fields.text(u'备注', size=32, readonly=True, states={'draft': [('readonly', False),]}),
        'line_ids': fields.one2many('inspection.line','order_id', u'明细',),
        'res_id': fields.reference(u'源单', selection=Quality_ref_selection, copy=False),
        'return_picking_id': fields.many2one('stock.picking', u'退货单', readonly=True),
        'return_inovice_id': fields.many2one('account.invoice', u'退款单', readonly=True),
        # ==========1201
        # 'return_amount': fields.float(u'扣款金额'),
        'return_amount': fields.float(u'扣款金额', readonly = True, states = {'draft': [('readonly', False), ]}),
        #'need_return': fields.boolean(u'需要退货'),
        #'need_return_money'

        # ==========multi company
        # 'company_id': fields.many2one('res.company', readonly=True, string=u'公司'),
    }

    _defaults = {
        'name': lambda *a: time.strftime('%Y%m%d%H%M%S'),
        'state': 'draft',

        # ==========multi company
        # 'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    }
    def print_iqc_report(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'mtlcs_quality.iqc_report', context=context)

    def unlink(self, cr, uid, ids, context=None):
        for data in self.read(cr, uid, ids, ['state']):
            if data['state'] not in ['draft', 'cancel']:
                raise osv.except_osv(('Error'), (u"非草稿、取消状态不可删除"))
        return super(quality_inspection_order, self).unlink(cr, uid, ids, context=context)

    def have_ng(self, inspection, context=None):
        for line in inspection.line_ids:
            if line.qty_ng:
                return True
        return False

    def have_ad(self, inspection, context=None):
        for line in inspection.line_ids:
            if line.qty_accept_deviation:
                return True
        return False

    def have_return(self, inspection, context=None):
        for line in inspection.line_ids:
            if line.qty_return:
                return True
        return False

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids[0], context=None)
        self.write(cr, uid, ids, {'user_id': uid}, context=context)

        if self.have_ng(order):
            self.write(cr, uid, ids, {'state': 'w_quality_manager', }, context=context)
        else:
            self.action_done(cr, uid, ids, context=context)
        return True

    def quality_manager_approve(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids[0], context=None)
        self.write(cr, uid, ids, {'state': 'w_purchase'}, context=context)

    def purchase_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'w_make_return'}, context=context)

    def return_processed(self, cr, uid, ids, context=None):
        o = self.browse(cr, uid, ids[0], context=context)

        if self.have_return(o) and not o.return_picking_id:
            raise Warning(u'有退货数，请创建退货单')
        if self.have_ad(o) and not o.return_inovice_id:
            raise Warning(u'有特采数，请创建退款单')
        self.action_done(cr, uid, ids, context=context)
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def make_invoice_return(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        p = self.browse(cr, uid, ids[0], context=context)
        if p.return_inovice_id:
            raise Warning(u'已创建退款，不可重复创建')
        if not self.have_ad(p):
            raise Warning(u'扣款，特采数量不能为空')
        if not p.return_amount:
            raise Warning(u'请输入扣款金额')
        ctx = context.copy()
        ctx.update({
            'type':'in_refund',
        })
        line_data = [(0 ,0, {
            'name': p.name,
            'quantity': 1,
            'price_unit': p.return_amount,
        })]
        data = {
            'account_id': p.partner_id.property_account_payable.id,
            'partner_id': p.partner_id.id,
            'type': 'in_refund',
            'origin': p.name,
            'invoice_line':line_data,
        }
        invoice_id = invoice_obj.create(cr, uid, data, context=ctx)
        self.write(cr, uid, p.id, {'return_inovice_id': invoice_id,}, context=context)
        return True

    def make_picking2ng(self, cr, uid, ids, context=None):
        inspection = self.browse(cr, uid, ids[0], context=context)
        if inspection.return_picking_id:
            raise Warning('已创建退货单，不可重复创建')
        if not self.have_return(inspection, context=context):
            raise Warning('没有退货数，不能入不合格仓')

        pick_obj = self.pool['stock.picking']
        type_stock2ng = self.pool['stock.picking.type'].browse_by_ref(cr, uid, 'stock2ng', context=context)

        moves = []

        for line in inspection.line_ids:
            moves.append((0, 0, {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty_return,
                'product_uom': line.product_id.uom_id.id,
                'location_id': type_stock2ng.default_location_src_id.id,
                'location_dest_id': type_stock2ng.default_location_dest_id.id,
                'price_unit': line.move_id.price_unit,
            }))

        data = {
            'partner_id': inspection.partner_id.id,
            'origin': inspection.partner_id.name,
            'picking_type_id': type_stock2ng.id,
            'move_lines': moves,
            'invoice_state': 'none',
        }
        pick_id = pick_obj.create(cr, uid, data, context=context)
        pick_obj.make_next_picking(cr, uid, [pick_id], context=context)
        self.write(cr, uid, inspection.id, {'return_picking_id':pick_id})
        return True




class inspection_line(osv.osv):
    _name = 'inspection.line'

    def _compute_qty(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if field_name == 'qty_ng':
                res[line.id] = line.qty - line.qty_ng
            elif field_name == 'qty_return':
                res[line.id] = line.qty_ng - line.qty_accept_deviation
        return res

    _columns = {
        'order_id': fields.many2one('quality.inspection.order', 'Inspection Order',),
        'product_id':fields.many2one('product.product', u'产品'),
        'uom_id': fields.many2one('product.uom', u'单位'),
        'qty': fields.float(u'数量'),
        'qty_ok': fields.function(_compute_qty, type='float', string=u'合格数'),
        'qty_ng': fields.float(u'不合格数'),
        'qty_accept_deviation': fields.float(u'特采数'),
        'qty_return': fields.function(_compute_qty, type='float', string=u'退货数'),
        'note': fields.char(u'说明', char=32),
        'unqualified_ids': fields.many2many('unqualified.item', 'ref_inspect_line_unqualified', 'line_id', 'item_id', string=u'不合格项'),
        'move_id': fields.many2one('stock.move', 'Move'),
    }

    _sql_constraints = [
        ('check_qty_ng_1', 'CHECK(qty_ng>=0)', u'不合格数量不能小于0'),
        ('check_qty_ng_2', 'CHECK(qty_accept_deviation>=0)', u'特采数数量不能小于0'),
        ('check_qty_ng_3', 'CHECK(qty>=qty_ng)', u'不合格数量不能大于检查数量'),
        ('check_qty_ng_4', 'CHECK(qty_accept_deviation<=qty_ng)', u'特采数不能大于不合格数量'),
    ]


class unqualified_item(osv.osv):
    _name = 'unqualified.item'
    _columns = {
        'name': fields.char(u'名称', required=True,),
        'code': fields.char(u'代码', required=True,),
    }

    _sql_constraints = [
        ('uniq_code', 'unique(code)', u'编码必须唯一'),
    ]



######################################################################
