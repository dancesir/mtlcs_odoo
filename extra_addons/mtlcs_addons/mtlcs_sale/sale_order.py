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
from openerp import models, api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID

from openerp.addons.sale.sale import sale_order as Sale_Order

SO_State_Old = Sale_Order._columns['state'].selection
MTL_SO_State = [
    ('w_director', u'待主管'),
    ('w_inspector', u'待销售总监'),
    ('w_send', u'待发送'),
    # sent（, u'待客户回签'),
    # progress
]
SO_State = SO_State_Old[:1] + MTL_SO_State + SO_State_Old[1:]
Sale_Production_Batch = [('draft', u'草稿'), ('w_director', u'待主管'), ('done', u'完成'), ]


class sale_order_line_batch(osv.osv):
    _name = 'sale.order.line.batch'

    def _compute_qty_no_production(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for b in self.browse(cr, uid, ids, context=context):
            res[b.id] = b.qty - sum([x.product_qty for x in b.production_ids])
        return res

    _columns = {
        'name': fields.char(u'销售投产批次', size=32),
        'state': fields.selection(Sale_Production_Batch, u'状态', readonly=True),
        'sol_id': fields.many2one('sale.order.line', '销售明细'),
        'qty': fields.float(u'数量'),
        'order_id': fields.related('sol_id', 'order_id', type='many2one', relation='sale.order', string=u'销售订单', readonly=True),
        'price_id': fields.related('sol_id', 'price_id', type='many2one', relation='pcb.price', string=u'报价单', readonly=True),
        'info_id': fields.related('price_id', 'info_id', type='many2one', relation="pcb.info", string=u'用户单', readonly=True),
        'product_id': fields.related('price_id', 'product_id', type='many2one', relation="product.product", string=u'档案号', readonly=True),
        'production_ids': fields.one2many('mrp.production', 'batch_id', 'Production'),
        'qty_no_production': fields.function(_compute_qty_no_production, type='float', store=True, string=u'未排产数量', readonly=True),
    }

    _defaults = {
        'name': lambda self, cr, uid, ctx: self._default_name(cr, uid, context=ctx),
        'state': 'draft',
    }

    def create(self, cr, uid, values, context=None):
        qty = values.get('qty', 0)
        if 'qty_no_production' not in values:
            values.update({'qty_no_production': values['qty']})
        sol = self.pool['sale.order.line'].browse(cr, uid, values.get('sol_id'), context=context)
        if qty > sol.qty_no_batch:
            raise Warning('批次数量不能大于未投产数量')
        return super(sale_order_line_batch, self).create(cr, uid, values, context=context)

    def _default_name(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').get(cr, uid, 'sale.production.batch')

    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'w_director'}, context=context)

    def approve_director(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def make_mrp_production(self, cr, uid, ids, context=None):
        production_obj = self.pool['mrp.production']
        bom_obj = self.pool['mrp.bom']
        batch = self.browse(cr, uid, ids, context=context)
        bom_ids = bom_obj.search(cr, uid, [('product_id', '=', batch.product_id.id)], context=context, limit=1)
        bom_id = bom_ids and bom_ids[0] or False
        bom = bom_obj.browse(cr, uid, bom_id, context=context)
        data = {
            'product_id': batch.product_id.id,
            'product_qty': batch.qty,
            'product_uom': batch.sol_id.product_uom.id,
            # 'date_planned': 1,
            'bom_id': bom.id,
            'routing_id': bom.routing_id.id,
            'batch_id': batch.id,
        }
        production_obj.create(cr, uid, data, context=context)
        return True


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _compute_qty_no_batch(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for sol in self.browse(cr, uid, ids, context=context):
            res[sol.id] = sol.product_uom_qty - sum([x.qty for x in sol.batch_ids])
        return res

    _columns = {
        'price_id': fields.many2one('pcb.price', u'报价单', required=False, ondelete="restrict"),
        'batch_ids': fields.one2many('sale.order.line.batch', 'sol_id', string=u"投产批次号"),
        'qty_no_batch': fields.function(_compute_qty_no_batch, type='float', string=u'销售未投数量', store=True, readonly=True),
        'once_fee_sol_id': fields.many2one('sale.order.line', u'From Line', help='Once Fee come form which SOL?'),
    }
    _defaults = {
    }

    def make_batch(self, cr, uid, ids, context=None):
        sol = self.browse(cr, uid, ids[0], context=context)
        if sol.qty_no_batch > 0:
            self.write(cr, uid, sol.id, {'batch_ids': [(0, 0, {
                'qty': sol.qty_no_batch,
            })]})
        else:
            raise Warning(u'未投产量已经为零')
        return True

    def make_part_batch(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': u'创建： 投产批次号',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'wizard.sale.order',
            'target': 'new',
        }


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def reset_draft(self):
        # go from canceled state to draft state
        for order in self:
            if order.state != 'cancel':
                raise Warning(u'非取消状态下，不能重置为草稿')
            order.order_line.write({'state': 'draft'})
            order.procurement_group_id.sudo().unlink()
            for line in order.order_line:
                line.procurement_ids.sudo().unlink()
            order.write({'state': 'draft'})
            order.delete_workflow()
            order.create_workflow()
        return True


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _get_default_warehouse(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not warehouse_ids:
            return False
        return warehouse_ids[1]

    _columns = {
        'state': fields.selection(SO_State, "State"),
        'account_touched': fields.boolean(u'财务已签收'),
        'is_special_approved': fields.boolean(u'是特批单'),
        'is_special_finish': fields.boolean(u'合同已追回'),
    }

    _defaults = {
        'warehouse_id': _get_default_warehouse,
    }


    def user_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_director'}, context=context)
        return True

    def director_approve(self, cr, uid, ids, context=None):
        to_state = 'w_send'
        so = self.browse(cr, uid, ids[0], context=context)
        for line in so.order_line:
            if line.price_id.amount > 20000:
                to_state = 'w_inspector'
        self.write(cr, uid, so.id, {'state': to_state}, context=context)
        return True

    def inspector_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_send'}, context=context)
        return True

    def send_approve(self, cr, uid, ids, context=None):
        # wkf quotation_sent
        self.signal_workflow(cr, uid, ids, 'quotation_sent')
        return True

    def customer_approve(self, cr, uid, ids, context=None):
        assert  len(ids) == 1
        # wkf order_confirm
        self.signal_workflow(cr, uid, ids, 'order_confirm')
        return True

    def special_approve(self, cr, uid, ids, context=None):
        # wkf order_confirm
        self.signal_workflow(cr, uid, ids, 'order_confirm')
        self.write(cr, uid, ids, {'is_special_approved': True})
        return True

    def special_finish(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'is_special_finish': True}, context=context)
        return True

    def account_touch(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'account_touched': True}, context=context)

    def action_wait(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        so = self.browse(cr, uid, ids[0], context=context)
        self.check_make_product(cr, uid, so, context=context)
        return res

    def _get_pprices(self, cr, uid, so_id,  context=None, sale_order=None, return_type='obj'):
        # return_type ['obj','id']
        so = sale_order or self.browse(cr, uid, so_id, context=context)
        res = set([x.price_id for x in so.order_line if x.price_id])
        if return_type == 'id':
            res = [x.id for x in res]
        return res

    def check_make_product(self, cr, uid, so, context=None):
        info_obj = self.pool.get('pcb.info')
        sol_obj = self.pool.get('sale.order.line')
        pdt_obj = self.pool.get('product.product')

        pprices = self._get_pprices(cr, uid, [], sale_order=so)
        for pprice in pprices:
            if pprice.receive_id.type == 'new':
                product_id = info_obj.make_product(cr, uid, None, info=pprice.info_id)
                name = pdt_obj.name_get(cr, uid, product_id)[0][1]
                sol_obj.write(cr, uid, pprice.sol_id.id, {
                    'product_id': product_id,
                    'name': name,
                }, context=context)
        return True


class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
        'batch_id': fields.many2one('sale.order.line.batch', u"订单投产批次", ),
    }
    _defaults = {
    }

    def create(self, cr, uid, values, context=None):
        qty = values.get('product_qty', 0)
        batch_id = values.get('batch_id')
        if batch_id:
            batch = self.pool['sale.order.line.batch'].browse(cr, uid, batch_id, context=context)
            if qty > batch.qty_no_production:
                raise Warning(u'生产数量不能大于未排产数量')
        return super(mrp_production, self).create(cr, uid, values, context=context)

        ######################################################################################
