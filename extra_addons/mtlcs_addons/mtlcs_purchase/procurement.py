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
import datetime
from openerp.tools.translate import _
from openerp.osv import fields, osv
import openerp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.exceptions import Warning
from openerp.addons.procurement.procurement import procurement_order as Procurement_Order
from openerp.addons.mtlcs_product.product import Product_ABC
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

Preparation_Order_State = [
    ('draft', u'草稿'),
    ('w_production_chief_inspector', u'待制造总监'),
    ('w_account', u'待财务'),
    ('w_chairman', u'待董事长'),
    ('w_purchase', u'待采购'),
    ('done', u'完成'),
    ('cancel', u'取消')
]

Preparation_Order_Type = [
    ('plan', u'常规/计划型'),
    ('manual', u'非常规/人工'),
    ('office', u'办公用品'),
    ('maintain', u'维修'),
    ('equipment', u'设备/工程'),
    ('outside', u'外协'),
]


class preparation_order(osv.osv):
    """
    prepare procurement order for PR
    """
    _name = "preparation.order"
    _order = 'id desc'
    _inherit = ['mail.thread', 'approve.log.thread']
    _description = "preparation.order"
    # ==========1121
    _approve_log = ['state']

    _track = {
        'state': {
            #'mtlcs_purchase.preparation_order_draft': lambda self, cr, uid, obj, ctx=None: obj.state == 'draft',
            'mtlcs_purchase.preparation_order_w_production_chief_inspector': lambda self, cr, uid, obj,
                                                                                    ctx=None: obj.state == 'w_production_chief_inspector',
            'mtlcs_purchase.preparation_order_w_account': lambda self, cr, uid, obj, ctx=None: obj.state == 'w_account',
            'mtlcs_purchase.preparation_order_w_chairman': lambda self, cr, uid, obj, ctx=None: obj.state == 'w_chairman',
            'mtlcs_purchase.preparation_order_w_purchase': lambda self, cr, uid, obj, ctx=None: obj.state == 'w_purchase',
            'mtlcs_purchase.preparation_order_done': lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
        },
    }

    def _is_started_requisition(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for o in self.browse(cr, uid, ids, context=context):
            res[o.id] = any([x.state != 'confirmed' for x in o.procurement_ids])
        return res

    _columns = {
        'name': fields.char(u'申购单', size=32, readonly=True, states={'draft': [('readonly', False), ]}),
        'type': fields.selection(Preparation_Order_Type, u'类型', readonly=True, states={'draft': [('readonly', False), ]}),
        'ppm_id': fields.many2one('production.plan.month', u'月生产计划', readonly=True, states={'draft': [('readonly', False)]}),
        'procurement_ids': fields.one2many('procurement.order', 'preparation_id', u'需求', readonly=True,
                                           states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', u'部门', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', u'申请人', readonly=True, states={'draft': [('readonly', False)]}),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'create_date': fields.datetime(u'创建时间', readonly=True),
        'state': fields.selection(Preparation_Order_State, u'状态'),
        # ==========1201
        # 'note': fields.text('Note'),
        'note': fields.text('Note',readonly=True, states={'draft': [('readonly', False)]}),
        'unconventional': fields.boolean(u'非常规', readonly=True),
        # 'purchase_approve_time': fields.datetime(u'采购接单时间'),
        # ==========1126
        # 'rule_id': fields.many2one('procurement.rule', u'规则'),
        'rule_id': fields.many2one('procurement.rule', u'规则', readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_id': fields.related('rule_id', 'warehouse_id', type="many2one", relation='stock.warehouse', string=u'仓库', readonly=True),
        'location_id': fields.related('rule_id', 'location_id', type="many2one", relation='stock.location', string=u'库位', readonly=True),
        'is_started_requisition': fields.function(_is_started_requisition, type='boolean', string=u'Requisition Started'),
        'company_id': fields.many2one('res.company', u'公司'),

    }

    # ==========multi company
    # _defaults = {
    #     'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    # }

    _sql_constraints = [
        ('uniq_name', 'unique(name)', u'申购单号不能重复'),
        ('ppm_uniq', 'unique(ppm_id)', u'月生产计划不能重复'),
    ]


    def _default_name(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').get(cr, uid, 'preparation.order')

    def default_get(self, cr, uid, field_name, context=None):
        res = super(preparation_order, self).default_get(cr, uid, field_name, context=context)
        rule_obj = self.pool['procurement.rule']
        rule_ids = rule_obj.search(cr, uid, [('action', '=', 'buy')], context=context, limit=1)
        rule = rule_obj.browse(cr, uid, rule_ids[0], context=context)
        res.update({
            'name': '/',
            'state': 'draft',
            'rule_id': rule.id,
            'type': 'manual',
            'user_id': uid,
            'department_id': self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context).default_department_id.id,
            'create_date': fields.datetime.now(),
            # ==========multi company
            'company_id': 1,
            # 'company_id':self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
            'location_id': rule.location_id.id,
            'warehouse_id': rule.warehouse_id.id}
        )
        return res

    def onchange_uer(self, cr, uid, ids, user_id, context=None):
        department_id = False
        if user_id:
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, user_id, context=context)
            department_id = user.default_department_id and user.default_department_id.id or False
        return {'value': {'department_id': department_id}}

    #rule
    def copy(self, cr, uid, id, default=None, context=None):
        # default['name'] = self._default_name(cr, uid, context=context)
        return super(preparation_order, self).copy(cr, uid, id, default=default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for data in self.read(cr, uid, ids, ['state']):
            if data['state'] not in ['draft', 'cancel']:
                raise osv.except_osv(_('Error'), _(u"非草稿、取消状态不可删除"))
        return super(preparation_order, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'preparation.order')
        return super(preparation_order, self).create(cr, uid, vals, context)

    def confirm(self, cr, uid, ids, context=None):
        for preparation in self.browse(cr, uid, ids, context=context):
            if not preparation.procurement_ids:
                raise Warning(u'物料需求不能为空')
            for procurement in preparation.procurement_ids:
                if procurement.product_qty <= 0:
                    raise Warning(u'数量不能为0')
        self.check_unconventional(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'w_production_chief_inspector'}, context=context)
        return True

    def production_chief_inspector_approve(self, cr, uid, ids, context=None):
        for preparation in self.browse(cr, uid, ids, context=context):
            to_state = preparation.unconventional and 'w_account' or 'w_purchase'
            self.write(cr, uid, preparation.id, {'state': to_state})
        return True

    def account_approve(self, cr, uid, ids, context=None):
        for preparation in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, preparation.id, {'state': 'w_chairman'})
        return True

    def chairman_approve(self, cr, uid, ids, context=None):
        for preparation in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, preparation.id, {'state': 'w_purchase'})
        return True

    def purchase_approve(self, cr, uid, ids, context=None):
        self.action_done(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'done', 'purchase_approve_time': fields.datetime.now()}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        procurement_obj = self.pool['procurement.order']
        for preparation in self.browse(cr, uid, ids, context=context):
            procurement_obj.action_confirm(cr, uid, [x.id for x in preparation.procurement_ids], context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        procurement_obj = self.pool['procurement.order']
        for preparation in self.browse(cr, uid, ids, context=context):
            proc_ids = [x.id for x in preparation.procurement_ids]
            procurement_obj.cancel(cr, uid, proc_ids, context=context)
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        procurement_obj = self.pool['procurement.order']
        for preparation in self.browse(cr, uid, ids, context=context):
            proc_ids = [x.id for x in preparation.procurement_ids]
            procurement_obj.reset_to_draft(cr, uid, proc_ids, context=context)
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def check_unconventional(self, cr, uid, ids, context=None):
        """
        any product is unconventional and account_total > 2000
        """
        preparation = self.browse(cr, uid, ids[0], context=context)
        total = 0
        unconventional = False
        limit = self.pool.get("ir.config_parameter").get_param(cr, uid, "unconventional_purchase_limit",
                                                               context=context)
        limit = max(int(limit), 1)
        for line in preparation.procurement_ids:
            total += line.product_qty * line.product_id.standard_price
            if line.product_id.unconventional:
                unconventional = True

        unconventional = (unconventional and total > limit) and True or False
        self.write(cr, uid, preparation.id, {'unconventional': unconventional})
        return True


    def get_relation_product_price(self, cr, uid, ids, context=None):
        '''
        get the relation products prices
        '''
        relation_obj = self.pool.get('relation.product.group')
        info_obj = self.pool.get('pricelist.partnerinfo')
        pr = self.browse(cr, uid, ids[0], context=context)
        p_ids = [x.product_id.id for x in pr.procurement_ids]
        relation_tmpl_ids = relation_obj.get_relation_product(cr, uid, p_ids, context=context)['relation_tmpl']
        info_ids = info_obj.search(cr, uid, [('tmpl_id', 'in', relation_tmpl_ids)], order='suppinfo_id', context=context)
        return {
            'domain': [('id', 'in', info_ids)],
            'name': _(u'相关物料价格信息'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'pricelist.partnerinfo',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def batch_select_product(self, cr, uid, ids, context=None):
        p = self.browse(cr, uid, ids[0], context=context)
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mtlcs_product', 'product_tree_view_for_preparation_order')[1]
        ctx = context.copy()
        ctx.update({
            'add_to_preparation_order': 1,
            'default_state': 'draft',
            'default_rule_id': p.rule_id.id,
            'default_location_id': p.location_id.id,
            'default_warehouse_id': p.warehouse_id.id,
            'default_origin': p.name,
        })
        return {
            'name': _(u'添加明细物料'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'domain': [('purchase_ok', '=', True)],
            'flags': {'selectable': False, },
            'context': ctx,
            # 'target': 'new',
        }

    def get_product_qty(self, cr, uid, ids, context=None):
        preparation = self.browse(cr, uid, ids[0], context=context)
        product_ids = [line.product_id.id for line in preparation.procurement_ids]
        return {
            'domain': [('id', 'in', product_ids)],
            'name': _(u'查看产品数量'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def get_purchase_order_line(self, cr, uid, ids, context=None):
        pol_obj = self.pool.get('purchase.order.line')
        preparation = self.browse(cr, uid, ids[0], context=context)
        product_ids = [line.product_id.id for line in preparation.procurement_ids]
        pol_ids = pol_obj.search(cr, uid, [('product_id', 'in', product_ids),
                                           ('state', 'in', ['done', 'confirmed', 'approved'])], order='product_id',
                                 context=context)
        return {
            'domain': [('id', 'in', pol_ids)],
            'name': _(u'历史采购明细'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order.line',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def get_history_procurement(self, cr, uid, ids, context=None):
        ''''''
        procurementl_obj = self.pool.get('procurement.order')
        preparation = self.browse(cr, uid, ids[0], context=context)
        product_ids = [line.product_id.id for line in preparation.procurement_ids]
        pol_ids = procurementl_obj.search(cr, uid, [('product_id', 'in', product_ids),
                                                    ('preparation_id', '!=', preparation.id),
                                                    ('preparation_id.create_date', '<', preparation.create_date)
                                                    ], order='product_id', context=context)

        return {
            'domain': [('id', 'in', pol_ids)],
            'name': _(u'历史申购记录'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def make_procurement_by_ppm(self, cr, uid, ids, context=None):
        """
        TODO: 请购量 = （标准 * 下月生产计划） + 安全库存 - 现有库存  +  （当月剩余天数 * 当月品均每日用量）
        """
        standard_obj = self.pool.get('material.consumption.standard')
        move_obj = self.pool.get("stock.move")
        uom_obj = self.pool.get("product.uom")
        rule_obj = self.pool.get('procurement.rule')
        model_obj= self.pool.get('ir.model.data')


        cr.execute("SELECT product_id, product_min_qty FROM stock_warehouse_orderpoint WHERE active = 't'")
        res = cr.fetchall()
        point_dict = dict(res)

        # po_lead = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.po_lead or 1
        # date_planned = (datetime.datetime.now() + datetime.timedelta(days=po_lead)).strftime(DTF)

        preparation = self.browse(cr, uid, ids[0], context=context)
        ppm = preparation.ppm_id
        rule = preparation.rule_id
        std_ids = standard_obj.get_normal_ids(cr, uid, context=context)
        standards = standard_obj.browse(cr, uid, std_ids, context=context)
        dict_need_qty = standard_obj.get_need_qty(cr, uid, std_ids, area=ppm.value, standards=standards, context=context)

        # ctx = context.copy()
        # ctx.update({
        #     'rule_id': preparation.rule_id.id,
        #     'location_id': preparation.location_id.id,
        #     'warehouse_id': preparation.warehouse_id.id,
        # })

        # rule_id_need_iqc = rule_obj.search(cr, uid, [('code','=','buy_need_iqc'),('action','=','buy'),])
        # rule_id_no_iqc = rule_obj.search(cr, uid, [('code','=','buy_no_iqc'),('action','=','buy'),])
        # rule_id_need_iqc = rule_id_need_iqc and rule_id_need_iqc[0] or None
        # rule_id_no_iqc = rule_id_no_iqc and rule_id_no_iqc[0] or None
        # if not (rule_id_need_iqc or rule_id_no_iqc):
        #     raise Warning(u"Not found the Rule.")
        #
        # rule_need_iqc = rule_obj.browse(cr, uid, rule_id_need_iqc, context=context)
        # rule_no_iqc = rule_obj.browse(cr, uid, rule_id_no_iqc, context=context)

        procurement_data = [(5, 0)]
        for std in standards:
            plan_qty = dict_need_qty[std.id]
            if plan_qty > 0:
                product = std.product_id
                uom_id = product.uom_id.id
                po_uom_id = product.uom_po_id.id
                product_qty = uom_obj._compute_qty(cr, uid, uom_id, plan_qty, po_uom_id, round=False, rounding_method='UP')
                data = {
                    'name': '%s %s' % (product.default_code, ppm.name),
                    'product_id': product.id,
                    'plan_qty': plan_qty,
                    'qty': plan_qty,
                    'product_qty': product_qty,
                    'product_uom': po_uom_id,
                    'state': 'draft',
                    'rule_id': rule.id,
                    'location_id':rule.location_id.id,
                    'warehouse_id': rule.warehouse_id.id
                }
                procurement_data.append((0, 0, data))

        self.write(cr, uid, preparation.id, {'procurement_ids': procurement_data}, context=context)
        return True

    def rouding_product_qty(self, cr, uid, ids, context=None):
        procurement_obj = self.pool.get('procurement.order')
        p = self.browse(cr, uid, ids[0], context=context)
        procurement_ids = [x.id for x in p.procurement_ids]
        procurement_obj.rouding_product_qty(cr, uid, procurement_ids, context=context)
        return True

    def run_month_scheduler(self, cr, uid, use_new_cursor=False, year_month=None, company_id=False, context=None):
        '''
        25/month, auot to create a plan preparation order

        '''
        _logger.info('Start run_month_scheduler')

        context = context or {}
        month_obj = self.pool.get('year.month')
        ppm_obj = self.pool.get('production.plan.month')
        try:
            if use_new_cursor:
                cr = openerp.registry(cr.dbname).cursor()

            next_month = month_obj.get_next_month(cr, uid, context=context)
            if not next_month:
                _logger.error('not found next month')
                return True

            # search next month production plan
            next_ppm_ids = ppm_obj.search(cr, uid, [('month_id','=',next_month[0]), ('state','=', 'done')], context=context)
            next_ppm_id = next_ppm_ids and next_ppm_ids[0] or False
            if not next_ppm_id:
                _logger.error('not found next ppm')
                return True

            # search the preparation is exist
            preparation_ids = self.search(cr, uid, [('ppm_id', '=', next_ppm_id)], context=context, limit=1)
            if preparation_ids:
                _logger.error('preparation exist, not need to create')
                return True
            else:
                # create preparation order, type is plan
                new_id = self.create(cr, uid, {
                    'type': 'plan',
                    'ppm_id': next_ppm_id,
                }, context=context)
                # calculation the procurement order
                self.make_procurement_by_ppm(cr, uid, [new_id], context=context)
                self.rouding_product_qty(cr, uid, [new_id], context=context)
                _logger.info('preparation create ok ID:%s' % new_id)

            if use_new_cursor:
                cr.commit()

        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass

        _logger.info('End run_month_scheduler')
        return {}

    def create_procurement_by_excel(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': u'物料需求Excel导入',
            'view_type': 'form',
            "view_mode": 'form',
            "res_model": 'excel.importor',
            'target': 'new',
        }


    def create_purchase_requisition(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids, context=None)
        wizard_obj = self.pool['procurement.make.requisition']
        ctx = context.copy()
        ctx.update({
            'active_model': 'procurement.order',
            'active_ids': [p.id for p in order.procurement_ids]
        })
        wizard_id = wizard_obj.create(cr, uid, {},  context=ctx)
        res = wizard_obj.apply(cr, uid, wizard_id, context=ctx)
        return res

    # ==========1126
    def action_print(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'mtlcs_purchase.report_preparation_order', context=context)


######################### Procuremnt

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def _compute_subtotal(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = p.product_qty * p.standard_price
        return res

    _columns = {
        'preparation_id': fields.many2one('preparation.order', string=u"申购单", ondelete="cascade"),
        'plan_qty': fields.float(u'计算数量', readonly=True),
        'qty': fields.float(u'申购数量-'),
        'uom_id': fields.related('product_id', 'uom_id', type='many2one', relation="product.uom", readonly=False, string=u"单位"),
        'preparation_state': fields.related('order_id', 'state', type="selection", selection=Preparation_Order_State, readonly=True,
                                            string=u"申购状态"),
        'create_time': fields.related('order_id', 'create_date', type='datetime', string=u'创建日期', readonly=True),
        'standard_price': fields.related('product_id', 'standard_price', type="float", readonly=True, string=u"成本价"),
        'price_subtotal': fields.function(_compute_subtotal, type='float', readonly=False, store=True, string=u'小计'),

        'qty_available': fields.related('product_id', 'qty_available', type='float', string=u'在库', readonly=True),
        'incoming_qty': fields.related('product_id','incoming_qty', type='float', string=u'在途', readonly=True),
        'procurement_qty': fields.related('product_id','procurement_qty',  type='float', string=u'待采购数量', readonly=True),

        'date_planned': fields.datetime(u'计划日期', required=True, select=True, track_visibility='onchange'),

        # ==========20170222
        'product_qty': fields.float(u'申购数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    required=True, states={'draft': [('readonly', False)]}, readonly=True),

    }

    _defaults = {
        #  'state': lambda self, cr, uid, ctx: self._default_state(cr, uid, context=ctx),
    }

    def rouding_product_qty(self, cr, uid, ids, context=None):
        uom_obj = self.pool.get('product.uom')
        for p in self.browse(cr, uid, ids, context=context):
            product_qty = p.product_qty
            product_uom = p.product_uom.id
            uom = p.uom_id.id
            int_product_qty = int(product_qty) + (product_qty % 1 and 1 or 0)
            qty = uom_obj._compute_qty(cr, uid, product_uom, int_product_qty, uom, round=False, rounding_method='UP')
            self.write(cr, uid, p.id, {'qty': qty, 'product_qty': int_product_qty}, context=context)

        return True

    def onchange_qty(self, cr, uid, ids, product_id, qty, product_qty, date_planned, fname='', context=None):
        """
        :param flage:  'uom_id' or  'uom_po_id'  make sure this change is baseon uom_id or uom_po_id
        """
        if not product_id:
            return None
        if not fname:
            raise osv.except_osv(_('Error!'), _(u'未发现单位标记'))
        model_obj = self.pool['ir.model.data']
        rule_obj = self.pool['procurement.rule']
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        pdt = product_obj.browse(cr, uid, product_id, context=None)
        uom_id = pdt.uom_id.id
        uom_po_id = pdt.uom_po_id.id

        # if pdt.need_iqc:
        #     rule_id = rule_obj.search(cr, uid, [('code','=','buy_need_iqc'),('action','=','buy'),])[0]
        # else:
        #     rule_id = rule_obj.search(cr, uid, [('code','=','buy_no_iqc'),('action','=','buy'),])[0]
        # rule = rule_obj.browse(cr, uid, rule_id, context=context)
        #value = {'rule_id': rule_id, 'location_id':rule.location_id.id, 'warehouse_id': rule.warehouse_id.id}

        date_planned = (datetime.datetime.now() + datetime.timedelta(days=pdt.purchase_period)).strftime(DTF)
        value = {}
        if fname == 'product_id':
            value.update({'date_planned': date_planned, 'qty': 0, 'product_qty': 0, 'uom_id': uom_id, 'product_uom': uom_po_id, 'name': pdt.name})
            # value.update({'qty': 0, 'product_qty': 0, 'uom_id': uom_id, 'product_uom': uom_po_id, 'name': pdt.name})
        # change qty of purchase unit
        if fname == 'product_qty':
            qty = uom_obj._compute_qty(cr, uid, uom_po_id, product_qty, uom_id, round=False, rounding_method='UP')
            value.update({'qty': qty})
        # change qty of base unit
        if fname == 'qty':
            product_qty = uom_obj._compute_qty(cr, uid, uom_id, qty, uom_po_id, round=False, rounding_method='UP')
            value.update({'product_qty': product_qty})

        return {'value': value}

    def get_cancel_ids(self, cr, uid, ids, context=None):
        cancel_ids = super(procurement_order, self).get_cancel_ids(cr, uid, ids, context=context)
        for pro in self.browse(cr, uid, cancel_ids, context=context):
            if pro.purchase_id and pro.purchase_id.state != 'cancel':
                raise osv.except_osv(_('Error!'), _(u'请先取消 采购单!'))
            if pro.requisition_id and pro.requisition_id.state != 'cancel':
                raise osv.except_osv(_('Error!'), _(u'请先取消 最近的请购!.'))
        return cancel_ids

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        '''
        because run_scheduler function have not a hook to fix the domain,so put the filter to context
        '''

        if context is None:
            context = {}
        if context.get('no_preparation'):
            args.append(('preparation_id','=',False))
        return super(procurement_order, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def run_scheduler(self, cr, uid, use_new_cursor=False, company_id = False, context=None):
        if not context:
            context = {}
        context.update({'no_preparation':True})
        return super(procurement_order, self).run_scheduler(cr, uid, use_new_cursor=use_new_cursor, company_id=company_id, context=context)


    def unlink(self, cr, uid, ids, context=None):
        procurements = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in procurements:
            if s['state'] in ['cancel','draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'),
                        _('Cannot delete Procurement Order(s) which are in %s state.') % s['state'])
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
