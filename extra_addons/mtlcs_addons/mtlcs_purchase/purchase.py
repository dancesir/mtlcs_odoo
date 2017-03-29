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
import logging
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.exceptions import Warning
from openerp.addons.purchase.purchase import purchase_order as Purchase_Order
from openerp.addons.purchase_requisition.purchase_requisition import purchase_requisition as Purchase_Requisition
from lxml import etree
import simplejson

_logger = logging.getLogger(__name__)

PO_State = Purchase_Order._columns['state'].selection
PO_State = PO_State[:1] + [('w_business_manager', u'待事业部经理'),('w_general_manager', u'待总经理'), ('w_send', u'待打印发送 '), ('w_account', u'待财务'), ] + PO_State[
                                                                                                             1:]

PR_State = Purchase_Requisition._columns['state'].selection
# ==========1206
# ==========170119
# PR_State = PR_State[:2] + [('w_purchase_manager', u'待采购主管')] + PR_State[2:]
PR_State = PR_State[:2] + [('w_purchase_manager', u'待采购主管'), ('w_business_manager', u'待事业部经理'),
                           ('w_general_manager', u'待总经理'), ] + PR_State[2:]

MTL_READONLY_STATES = {'w_send': [('readonly', True)]}
MTL_READONLY_STATES.update(Purchase_Order.READONLY_STATES)
# ==========1217
PRICE_METHOD = [('by_email', u'邮件'), ('by_tel', u'电话'), ('by_interview', u'面谈'), ('by_others', u'其他'), ]


class purchase_order(osv.osv):
    # ==========1121
    # _inherit = 'purchase.order'
    _inherit = ['purchase.order', 'mail.thread', 'approve.log.thread']
    _name = 'purchase.order'
    _approve_log = ['state']

    def _get_default_incoterm_id(self, cr, uid, context=None):
        return self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mtlcs_purchase', 'incoterm_SSM')[1]

    _columns = {
        # ==========1201
        'dongshuo_id': fields.integer(u'东烁ID', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection(PO_State, u'状态'),
        'is_bid_get': fields.boolean(u'意向订单', help=u"比价单中选择的采购单标记", readonly=True,
                                     states={'draft': [('readonly', False)]}),
        'payment_by_shipped': fields.boolean(u'收货完整才能付款', readonly=True, states={'draft': [('readonly', False)]}),
        'is_contract': fields.boolean(u'合同', readonly=True, states={'draft': [('readonly', False)]}),
        'date_order': fields.datetime(readonly=True, states={'draft': [('readonly', False)]}, ),
        'origin': fields.char(readonly=True, states={'draft': [('readonly', False)]}, ),
        'incoterm_id': fields.many2one('stock.incoterms', readonly=True, states={'draft': [('readonly', False)]}, ),
        'notes': fields.text(readonly=True, states={'draft': [('readonly', False)]}, ),
        'bid_validity': fields.date(readonly=True, states={'draft': [('readonly', False)]}, string=u'投标有效期' ),
        'requisition_id': fields.many2one('purchase.requisition', u'源单据', readonly=True,
                                          states={'draft': [('readonly', False)]}, ),
        'payment_term_id': fields.many2one('account.payment.term', readonly=True,
                                           states={'draft': [('readonly', False)]}, ),
        # 'fiscal_position': fields.many2one('account.fiscal.position', readonly=True, states={'draft': [('readonly', False)]},),

        # ==========1215
        'partner_id': fields.many2one('res.partner', u'供应商', required=True, states=MTL_READONLY_STATES,
                                      change_default=True, track_visibility='always'),
        'ref_supplier': fields.related('partner_id', 'ref_supplier', states=MTL_READONLY_STATES, type='char',
                                       string=u'编码', readonly=True, ),
        'partner_ref': fields.char(u'供应商单号', states=MTL_READONLY_STATES, copy=False, ),
        'pricelist_id': fields.many2one('product.pricelist', u'价格表', required=True, states=MTL_READONLY_STATES,
                                        help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities."),
        'picking_type_id': fields.many2one('stock.picking.type', u'交货到',
                                           help="This will determine picking type of incoming shipment", required=True,
                                           states=MTL_READONLY_STATES),
        'order_line': fields.one2many('purchase.order.line', 'order_id', u'产品', states=MTL_READONLY_STATES, copy=True),
        'location_id': fields.many2one('stock.location', u'目的地', required=True, domain=[('usage', '<>', 'view')],
                                       states=MTL_READONLY_STATES),
        # ==========1231
        'price_method': fields.selection(PRICE_METHOD, u'定价方式', readonly=True,
                                         states={'draft': [('readonly', False)]}, ),

         # ==========20170222
        'child_ids': fields.many2one('res.partner',  u'联系人', readonly=True, states={'draft': [('readonly', False)]},),
        'purchase_note': fields.text(u'采购询价过程', readonly=True, states={'draft': [('readonly', False)]},),
    }

    _defaults = {
        'payment_by_shipped': False,
        'incoterm_id': _get_default_incoterm_id,
        # ==========1223
        'price_method': 'by_tel',
    }

    def message_get_email_values(self, cr, uid, id, notif_mail=None, context=None):
        res = super(purchase_order, self).message_get_email_values(cr, uid, id, notif_mail=notif_mail, context=context)
        email_to = ','.join([p.email for p in notif_mail.partner_ids if p.email])
        res.update({'email_to': email_to})
        return res

    def onchange_is_contract(self, cr, uid, ids, is_contract, context=None):
        value = {'invoice_method': is_contract and 'order' or 'picking'}
        return {'value': value}

    # ==========20170302
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        value = super(purchase_order, self).onchange_partner_id( cr, uid, ids, partner_id, context=context)

        partner_obj = self.pool.get('res.partner')
        child_id = partner_obj.search(cr, uid, [('parent_id', '=', partner_id), ('parent_id', '!=', False)], limit=1)
        child_id = child_id and child_id[0] or False
        value.get('value').update({'child_ids': child_id})

        return value

    def _check_strict_supplier(self, cr, uid, po, context=None):
        for line in po.order_line:
            product = line.product_id
            if product.strict_supplier and po.partner_id.id not in [x.name.id for x in product.seller_ids]:
                raise Warning(u'%s 没有通过 %s 供应资质审核' % (po.partner_id.name, product.default_code))
        return True

    def _check(self, cr, uid, po, context=None):
        self._check_strict_supplier(cr, uid, po, context=context)
        if po.requisition_id and po.requisition_id.state not in ['open', 'done']:
            raise Warning(u'请先审核对应的比价单！')
        if po.requisition_id and not po.is_bid_get:
            raise Warning(u'次单据不是比价单据的意向订单')

    def purchase_manager_approve(self, cr, uid, ids, context=None):
        self._check(cr, uid, self.browse(cr, uid, ids[0], context=context), context=context)
        self.write(cr, uid, ids[0], {'state': 'w_general_manager'})
        # ==========1206
        # requisition_id = self.browse(cr, uid, ids[0], context=context).requisition_id.id
        # if requisition_id:
        #     requisition_obj = self.pool.get('purchase.requisition')
        #     requisition_obj.write(cr, uid, requisition_id, {'state': 'w_general_manager'})

        return True

    def general_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_send'})
        # ==========1206
        # requisition_id = self.browse(cr, uid, ids[0], context=context).requisition_id.id
        # if requisition_id:
        #     requisition_obj = self.pool.get('purchase.requisition')
        #     requisition_obj.write(cr, uid, requisition_id, {'state': 'open'})

        return True

    def send_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_account'})

        # self.make_approve_log(cr, uid, ids, state_to='w_account', context=context)
        return True

    def account_approve(self, cr, uid, ids, context=None):
        '''
         account is the who really approve the PO.
         then write back the pol.id to procurement.
        '''
        self.signal_workflow(cr, uid, ids, 'purchase_confirm', context=context)

        # self.make_approve_log(cr, uid, ids, state_to='purchase_confirm', context=context)
        # related the pol_id to procurement order
        proc_obj = self.pool.get('procurement.order')
        po = self.browse(cr, uid, ids[0], context=context)
        for pol in po.order_line:
            if pol.procurement_id:
                proc_obj.write(cr, uid, pol.procurement_id.id, {'purchase_line_id': pol.id}, context=context)
        return True

    def open_history_pol(self, cr, uid, ids, context=None):
        pol_obj = self.pool.get('purchase.order.line')
        po = self.browse(cr, uid, ids[0], context=context)
        pdt_ids = [x.product_id.id for x in po.order_line]
        domain = [('product_id', 'in', pdt_ids), ('state', 'in', ['done', 'confirmed'])]
        return pol_obj.open_lines(cr, uid, domain, context=context)

    def bid_get(self, cr, uid, ids, context=None):
        po = self.browse(cr, uid, ids[0], context=context)
        other_ids = [p.id for p in po.requisition_id.purchase_ids if p.id != po.id]
        self.write(cr, uid, other_ids, {'is_bid_get': False})
        self.write(cr, uid, ids, {'is_bid_get': True})

        # ==========1207
        self.price_abnormal(cr, uid, ids, po.requisition_id.id, context=context)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.requisition',
            'res_id': po.requisition_id.id,
            'type': 'ir.actions.act_window',
        }

    # ==========1208
    def price_abnormal(self, cr, uid, ids, requisition_id, context=None):

        pol_obj = self.pool.get('purchase.order.line')
        order_obj = self.browse(cr, uid, ids, context=context)
        requisition_obj = self.pool.get('purchase.requisition').browse(cr, uid, requisition_id, context=context)
        requisition_obj.is_price_abnormal = False
        for o in order_obj.order_line:
            pol_id = pol_obj.get_last_ids(cr, uid, pdt_ids=[o.product_id.id], context=None, limit=80)
            price_last = pol_obj.browse(cr, uid, pol_id, context=context).price_unit
            if o.price_unit > price_last and price_last > 0:
                requisition_obj.is_price_abnormal = True

    def action_print(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'mtlcs_purchase.report_purchase_order', context=context)

    def re_create_picking(self, cr, uid, ids, context=None):
        po = self.browse(cr, uid, ids[0])
        if po.picking_ids:
            raise Warning(u'使用此功能，请先联系管理员删除所有已创建的入库单')
        return self.action_picking_create(cr, uid, ids, context=context)


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'procurement_id': fields.many2one('procurement.order', u'需求单'),
        'unconventional': fields.related('product_id', 'unconventional', type='boolean', string=u'非常规', readonly=True),
        'strict_supplier': fields.related('product_id', 'need_iqc', type='boolean', string=u'需评供应商', readonly=True),

        # ==========1206
        'qty_available': fields.related('product_id', 'qty_available', type='float', string=u'在手数量', readonly=True),
        'virtual_available': fields.related('product_id', 'virtual_available', type='float', string=u'预测数量',
                                            readonly=True),
        'procurement_qty': fields.related('product_id', 'procurement_qty', type='float', string=u'需求数量', readonly=True),

    }

    def get_last_ids(self, cr, uid, pdt_ids=None, context=None, limit=80):
        if not pdt_ids:
            return False
        context = context and context or {}

        sql = """
select id
from (
    select id, product_id, create_date, row_number() over(partition by product_id order by create_date desc) as row_n
    from purchase_order_line where product_id = ANY (%s) and state in ('confirmed', 'done')
) pol
where row_n = 1;

        """
        cr.execute(sql, (pdt_ids,))
        return [x[0] for x in cr.fetchall()]


class product_supplierinfo(osv.osv):
    # ==========1121
    # _inherit = 'product.supplierinfo'
    _inherit = ['product.supplierinfo', 'mail.thread', 'approve.log.thread']
    _name = 'product.supplierinfo'
    _approve_log = ['state']

    _track = {
        'state': {
            'mtlcs_purchase.product_supplierinfo_w_chief_inspector': lambda self, cr, uid, obj,
                                                                            ctx=None: obj.state == 'w_chief_inspector',
            'mtlcs_purchase.product_supplierinfo_w_general_manager': lambda self, cr, uid, obj,
                                                                            ctx=None: obj.state == 'w_general_manager',
            'mtlcs_purchase.product_supplierinfo_done': lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
        },
    }
    _columns = {
        'active': fields.boolean('Active'),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'state': fields.selection(
            [('draft', u'草稿'), ('w_chief_inspector', u'待总监'), ('w_general_manager', u'待总经理'), ('done', u'完成'),
             ('cancel', u'取消')], 'State'),
    }

    _sql_constraints = [
        ('uniq_info', 'unique(name,product_tmpl_id)', u'物料供应商信息重复'),
    ]

    _defaults = {
        'active': True,
        'state': 'draft',
    }

    def confirm(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'w_chief_inspector'}, context=context)

        # self.make_approve_log(cr, uid, ids, state_to='w_chief_inspector', context=context)
        return True

    def chief_inspector_approve(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'w_general_manager'}, context=context)

        # self.make_approve_log(cr, uid, ids, state_to='w_general_manager', context=context)
        return True

    def general_manager_approve(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'done', 'active': True}, context=context)

        # self.make_approve_log(cr, uid, ids, state_to='done', context=context)
        return True

    def action_draft(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'draft', }, context=context)

        # self.make_approve_log(cr, uid, ids, state_to='draft', context=context)
        return True


class purchase_requisition_line(osv.osv):
    _inherit = 'purchase.requisition.line'

    # ==========1208
    def _supplier_amount(self, cr, uid, ids, fieldname, arg, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = len(p.product_id.seller_ids)
        return res

    _columns = {
        'procurement_id': fields.many2one('procurement.order', string=u'Procurement'),
        'origin': fields.related('procurement_id', 'origin', string=u'申购单', type='char', readonly=True),
        # ==========1220
        'qty_available': fields.related('product_id', 'qty_available', type='float', string=u'在库', readonly=True),
        'incoming_qty': fields.related('product_id', 'incoming_qty', type='float', string=u'在途', readonly=True),
        'virtual_available': fields.related('product_id', 'virtual_available', type='float', string=u'预测数',
                                            readonly=True),
        'procurement_qty': fields.related('product_id', 'procurement_qty', type='float', string=u'需求数', readonly=True),
        'supplier_amount': fields.related('product_id', 'supplier_amount', string=u'供应商数', type='integer',
                                          readonly=True),
        # 'price_method': fields.selection(PRICE_METHOD, u'定价方式', readonly=False, ),

        'highest_price': fields.related('product_id', 'highest_price', type='float', string=u'历史最高价', readonly=True),
        'bottom_price': fields.related('product_id', 'bottom_price', type='float', string=u'历史最低价', readonly=True),
        'last_price': fields.related('product_id', 'last_price', type='float', string=u'上次采购价', readonly=True),
    }

    _defaults = {
        # 'price_method': 'by_tel'
    }

    def create(self, cr, uid, values, context=None):
        return super(purchase_requisition_line, self).create(cr, uid, values, context=context)


class purchase_requisition(osv.osv):
    # ==========1121
    # _inherit = "purchase.requisition"
    _inherit = ['purchase.requisition', 'mail.thread', 'approve.log.thread']
    _name = 'purchase.requisition'
    _approve_log = ['state']

    _order = 'id desc'

    def _get_pol_ids(self, cr, uid, ids, file_name, arg=None, context=None):
        res = {}
        for req in self.browse(cr, uid, ids, context=context):
            po_s = [x for x in req.purchase_ids]
            line_ids = []
            for po in po_s:
                line_ids += [l.id for l in po.order_line]
            res[req.id] = line_ids
        return res

    def _get_info_ids(self, cr, uid, ids, file_name, arg=None, context=None):
        res = {}
        line_ids = []
        for req in self.browse(cr, uid, ids, context=context):
            line_ids += [x.product_id.id for x in req.line_ids]
        res[req.id] = line_ids

        return res

    _columns = {
        'state': fields.selection(PR_State, u'状态'),
        'pol_ids': fields.function(_get_pol_ids, type="one2many", relation="purchase.order.line", string='POL'),

        # ==========1231
        'is_price_abnormal': fields.boolean(u'采购价异常', readonly=True, ),
        'price_note': fields.text(u'价格异常说明', help=u'对采购价异常的说明', readonly=True,
                                  states={'draft': [('readonly', False)], 'in_progress': [('readonly', False)]}),
        'line_ids': fields.one2many('purchase.requisition.line', 'requisition_id', 'Products to Purchase',
                                    readonly=True,
                                    states={'draft': [('readonly', False)], 'in_progress': [('readonly', False)]},
                                    copy=True),
        'purchase_ids': fields.one2many('purchase.order', 'requisition_id', 'Purchase Orders', readonly=True,
                                        states={'draft': [('readonly', False)], 'in_progress': [('readonly', False)]}),
        # ==========1215
        'info_ids': fields.function(_get_info_ids, type="one2many", relation="product.product", string='信息'),
    }
    _defaults = {
        'exclusive': 'exclusive',
        # ==========1219
        # 'price_method': 'by_tel'

    }

    def get_relation_product_price(self, cr, uid, ids, context=None):
        relation_obj = self.pool.get('relation.product.group')
        info_obj = self.pool.get('pricelist.partnerinfo')

        pr = self.browse(cr, uid, ids[0], context=context)
        p_ids = [x.product_id.id for x in pr.line_ids]
        relation_tmpl_ids = relation_obj.get_relation_product(cr, uid, p_ids, context=context)['relation_tmpl']
        # ==========1206
        if relation_tmpl_ids:
            info_ids = info_obj.search(cr, uid, [('tmpl_id', 'in', relation_tmpl_ids)], context=context)
            return {
                'domain': [('id', 'in', info_ids)],
                'name': _(u'相关物料价格信息'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pricelist.partnerinfo',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            raise Warning(u'无相关物料价格信息')

    def _check(self, cr, uid, pr, context=None):
        po_obj = self.pool['purchase.order']
        if not pr.purchase_ids:
            raise Warning(u'请至少创建一张询价单')
        bid_po_ids = []
        min_total = None
        min_total_id = None
        bid_id = None

        for po in pr.purchase_ids:
            po_obj._check_strict_supplier(cr, uid, po, context=context)
            if po.is_bid_get:
                bid_po_ids.append(po.id)
                bid_id = po.id
                # ==========1231
                if len(po.payment_term_id) != 1:
                    raise Warning(u'意向供应商的支付条款不能为空：\n请先选择支付条款')

            # ==========1229
            if min_total == None:
                min_total = po.amount_total
                min_total_id = po.id

            if min_total is not None and po.amount_total < min_total:
                min_total = po.amount_total
                min_total_id = po.id

                # if not min_total or po.amount_total < min_total:
                #     min_total = po.amount_total
                #     min_total_id = po.id

        # ==========20170222检测供应商数量
        if len(set([po.partner_id.id for po in pr.purchase_ids])) == 1:
            raise osv.except_osv(_('Error!'), _(u'供应商数量必须大于一家'))

        if len(bid_po_ids) != 1:
            raise osv.except_osv(_('Error!'), _(u'必须标记意向订单，且只允许标记一个'))
        # ==========1209
        # if bid_id != min_total_id and not pr.description:
        if bid_id != min_total_id and not pr.price_note:
            raise Warning(u'没有选择价格最优的供应商作为意向订单，\n请填写价格异常说明')
        if pr.is_price_abnormal and not pr.price_note:
            raise Warning(u'高于上次采购价，\n请填写价格异常说明')

        return True

    def purchase_approve(self, cr, uid, ids, context=None):
        pr = self.browse(cr, uid, ids[0], context=context)
        self._check(cr, uid, pr, context=context)
        # ==========1209
        if not pr.price_note:
            self.write(cr, uid, ids[0], {'state': 'w_purchase_manager'}, context=context)
        else:
            self.write(cr, uid, ids[0], {'is_price_abnormal': True, 'state': 'w_purchase_manager', }, context=context)

        # self.make_approve_log(cr, uid, ids, state_to='w_purchase_manager', context=context)
        return True

    # def purchase_manager_approve(self, cr, uid, ids, context=None):
    #
    #     # self.make_approve_log(cr, uid, ids, state_to='open_bid', context=context)
    #     return self.signal_workflow(cr, uid, ids, 'open_bid', context=context)

    # ==========1208
    def purchase_manager_approve(self, cr, uid, ids, context=None):
        # ==========1229
        pr = self.browse(cr, uid, ids[0], context=context)
        self._check(cr, uid, pr, context=context)

        self.write(cr, uid, ids[0], {'state': 'w_business_manager'}, context=context)

        order_obj = self.pool.get('purchase.order')
        requisition_obj = self.browse(cr, uid, ids[0], context=context)
        order_id = order_obj.search(cr, uid, [('origin', '=', requisition_obj.name), ('is_bid_get', '=', True)])
        order_obj.write(cr, uid, order_id, {'state': 'w_business_manager'}, context=context)

        return True

    # ==========170119
    def business_manager_approve(self, cr, uid, ids, context=None):
        pr = self.browse(cr, uid, ids[0], context=context)
        self._check(cr, uid, pr, context=context)
        self.write(cr, uid, ids[0], {'state': 'w_general_manager'})

        order_obj = self.pool.get('purchase.order')
        requisition_obj = self.browse(cr, uid, ids[0], context=context)
        order_id = order_obj.search(cr, uid, [('origin', '=', requisition_obj.name), ('is_bid_get', '=', True)])
        order_obj.write(cr, uid, order_id, {'state': 'w_general_manager'}, context=context)

    def general_manager_approve(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('purchase.order')
        requisition_obj = self.browse(cr, uid, ids[0], context=context)
        order_id = order_obj.search(cr, uid, [('origin', '=', requisition_obj.name), ('is_bid_get', '=', True)])
        order_obj.write(cr, uid, order_id, {'state': 'w_send'}, context=context)
        order_cancel_id = order_obj.search(cr, uid, [('origin', '=', requisition_obj.name), ('is_bid_get', '=', False)])
        order_obj.write(cr, uid, order_cancel_id, {'state': 'cancel'}, context=context)

        return self.signal_workflow(cr, uid, ids, 'open_bid', context=context)

    # ===========20170302
    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        res = super(purchase_requisition, self).make_purchase_order(cr, uid, ids, partner_id, context=context)

        # 在创建的采购订单中设置默认联系人
        po_id = res.get(ids[0])
        po_obj = self.pool.get('purchase.order').browse(cr, uid, po_id, context=context)
        partner_obj = self.pool.get('res.partner')
        child_id = partner_obj.search(cr, uid, [('parent_id', '=', partner_id)], limit=1)
        child_id = child_id and child_id[0] or False

        po_obj.write({'child_ids':child_id})

        return res

    def auto_req(self, cr, uid, ids, context=None):
        req = self.browse(cr, uid, ids[0], context=context)
        supplier_ids = []
        for p in [x.product_id for x in req.line_ids]:
            for info in p.seller_ids:
                supplier_id = info.name.id
                if supplier_id not in supplier_ids:
                    supplier_ids.append(supplier_id)

        for supplier_id in supplier_ids:
            self.make_purchase_order(cr, uid, [req.id, ], supplier_id, context=context)
        return True

    # ==========20170303
    def report_purchase_history_price(self, cr, uid, ids, context=None):

        products = self.browse(cr, uid, ids, context=context).line_ids
        pro_ids = [p.product_id.id for p in products]

        return {
            'domain': [('product_id', 'in', pro_ids)],
            'name': _(u'前六次采购价格走势'),
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'report.purchase.history.price',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _prepare_purchase_order_line(self, cr, uid, requisition, requisition_line, purchase_id, supplier, context=None):
        res = super(purchase_requisition, self)._prepare_purchase_order_line(cr, uid, requisition, requisition_line,
                                                                             purchase_id, supplier, context=context)
        res.update({'procurement_id': requisition_line.procurement_id.id})
        return res

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        res = super(purchase_requisition, self)._prepare_purchase_order(cr, uid, requisition, supplier, context=context)
        res.update({
            'payment_term_id': supplier.property_supplier_payment_term and supplier.property_supplier_payment_term.id or False})
        return res

    def open_history_pol(self, cr, uid, ids, context=None):
        pol_obj = self.pool.get('purchase.order.line')
        req = self.browse(cr, uid, ids[0], context=context)
        pdt_ids = [x.product_id.id for x in req.line_ids]
        domain = [('product_id', 'in', pdt_ids), ('state', 'in', ['done', 'confirmed'])]
        return pol_obj.open_lines(cr, uid, domain, context=context)

    def open_product_line(self, cr, uid, ids, context=None):
        action = super(purchase_requisition, self).open_product_line(cr, uid, ids, context=context)
        action.update({'context': {}, 'target': 'new'})
        return action

    # ==========1126
    def action_print(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'mtlcs_purchase.report_purchase_requisition',
                                              context=context)



        # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
