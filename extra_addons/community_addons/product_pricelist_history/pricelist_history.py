# -*- coding: utf-8 -*-
import time
from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _
from openerp.exceptions import Warning


class price_adjust_order(osv.osv):
    # ==========1121
    _inherit = ['mail.thread', 'approve.log.thread']
    _name = 'price.adjust.order'
    _order = 'id'
    _approve_log = ['state']

    _columns = {
        'name': fields.char(u'调价单', size=16, readonly=True, states={'draft': [('readonly', False), ]}),
        'partner_id': fields.many2one('res.partner', u'供应商', required=True, readonly=True,
                                      states={'draft': [('readonly', False), ]}),
        'state': fields.selection(
            [('draft', u'草稿'), ('w_purchase_manager', u'待采购主管'), ('w_general_manager', u'待总经理'), ('done', u'完成')],
            u'状态'),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True, ),
        'create_date': fields.datetime(u'创建日期', readonly=True, ),
        'line_ids': fields.one2many('price.adjust.line', 'order_id', u'调价明细', readonly=True,
                                    states={'draft': [('readonly', False), ]}),
        'note': fields.text(u'备注', readonly=True, states={'draft': [('readonly', False), ]}),
    }

    _defaults = {
        'create_uid': lambda self, cr, uid, ctx: uid,
        'create_date': fields.datetime.now(),
        'state': 'draft',
        'name': time.strftime('%Y%m%d%H%M%S')
    }

    def unlink(self, cr, uid, ids, context=None):
        for i in self.browse(cr, uid, ids, context=context):
            if i.state != 'draft':
                Warning(u'不允许删除非草稿单据')
        return super(price_adjust_order, self).unlink(cr, uid, ids, context=context)

    # ==========1230
    def check_price(self, cr, uid, ids, context=None):
        if len(self.browse(cr, uid, ids, context=context).line_ids) == 0:
            raise Warning(u'明细内容不能为空！')
        for p in self.browse(cr, uid, ids, context=context).line_ids:
            if p.new_price <= 0 or p.new_price == p.old_price:
                raise Warning(u'请先更改或删除明细中的以下内容：\n1：新价格为0元的物料.\n2：新旧价格相同的物料')
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        # ==========1230
        self.check_price(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'w_purchase_manager'}, context=context)

    def purchase_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_general_manager'}, context=context)

    def general_manager_approve(self, cr, uid, ids, context=None):
        self.update_price(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def update_price(self, cr, uid, ids, context=None):
        partnerinfo_obj = self.pool['pricelist.partnerinfo']
        adjust_order = self.browse(cr, uid, ids, context=context)
        for line in adjust_order.line_ids:
            partnerinfo_obj.write(cr, uid, line.partnerinfo_id.id, {'price': line.new_price}, context=context)
        return True

    def auot_fill_line(self, cr, uid, ids, context=None):
        partnerinfo_obj = self.pool['pricelist.partnerinfo']
        order = self.browse(cr, uid, ids[0], context=context)
        info_ids = partnerinfo_obj.search(cr, uid, [('partner_id', '=', order.partner_id.id)], context=context)
        infos = partnerinfo_obj.browse(cr, uid, info_ids, context=context)

        line_ids = []
        if order.line_ids:
            line_ids = [(2, x.id) for x in order.line_ids]

        for info in infos:
            line_data = {
                'partnerinfo_id': info.id,
                'old_price': info.price,
                # ==========1231
                'new_price': info.price,
                # 'new_price':0.0
            }
            line_ids.append((0, 0, line_data))

        self.write(cr, uid, order.id, {'line_ids': line_ids}, context=context)
        return True

    # ==========1126
    def action_print(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'mtlcs_purchase.report_price_adjust_order',
                                              context=context)


class price_adjust_line(osv.osv):
    _name = 'price.adjust.line'
    _order = 'product_id,id'

    PRICE_STATE = [('init', u'-'), ('up', u'↑'), ('down', u'↓')]

    # ==========1118
    def _compute_old_price(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        partnerinfo_obj = self.pool['pricelist.partnerinfo']
        for p in self.browse(cr, uid, ids, context=context):
            old_price = partnerinfo_obj.browse(cr, uid, p.partnerinfo_id.id, context=context).price
            res[p.id] = old_price
        return res

    def _read_price_state(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = p.price_state
        return res

    _columns = {
        'order_id': fields.many2one('price.adjust.order', u'调价单'),
        'partner_id': fields.related('order_id', 'partner_id', type='many2one', relation='res.partner', readonly=True,
                                     string=u'供应商'),
        'partnerinfo_id': fields.many2one('pricelist.partnerinfo', u'价格信息'),
        # ==========1117
        # 'old_price': fields.float(string=u'原价', store=True, ),
        'old_price': fields.function(_compute_old_price, type='float', readonly=False, store=True, string=u'原价'),

        'new_price': fields.float(u'新价'),
        'product_id': fields.related('partnerinfo_id', 'product_id', relation='product.product', type='many2one',
                                     string=u'产品', readonly=True, ),
        'price': fields.related('partnerinfo_id', 'price', type='float', string='Price'),
        # start_time
        # end_time

        # ============20170102
        'price_state': fields.selection(PRICE_STATE, u'价格状态hide', ),
        'price_state_dis': fields.function(_read_price_state, string=u'价格状态', type='selection',
                                           selection=PRICE_STATE, ),
    }

    # ==========1116
    def onchange_partnerinfo_id(self, cr, uid, ids, partnerinfo_id, context=None):
        if not partnerinfo_id:
            return None
        value = {}
        partnerinfo_obj = self.pool.get('pricelist.partnerinfo')
        old_price = partnerinfo_obj.browse(cr, uid, partnerinfo_id, context=context).price
        value.update({'old_price': old_price, 'new_price': old_price, })
        return {'value': value}

    # ============20170104
    def onchange_new_price(self, cr, uid, ids, new_price, partnerinfo_id, context=None):
        if not new_price:
            return None
        value = {}

        partnerinfo_obj = self.pool.get('pricelist.partnerinfo')
        price_obj = self.browse(cr, uid, ids, context=context)

        old_price = (len(price_obj) == 0) and partnerinfo_obj.browse(cr, uid, partnerinfo_id,
                                                                     context=context).price or price_obj.old_price

        if old_price > new_price:
            value.update({'price_state': 'down', 'price_state_dis': 'down', })
        if old_price < new_price:
            value.update({'price_state': 'up', 'price_state_dis': 'up', })
        if new_price is None or old_price == new_price:
            value.update({'price_state': 'init', 'price_state_dis': 'init', })

        return {'value': value, }

#####################################################################################
