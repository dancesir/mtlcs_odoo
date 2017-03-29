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
from openerp.tools.translate import _

Receive_Type = [
    ('new', u'新单'),
    ('recast', u'复投无更改'),
    ('recast_change', u'复投有更改'),
    ('global_change', u'通用信息更改'),
    ('info_change', u'档案号信息更改'),
    ('online_change', u'客户在线更改'),
    ('pause', u'客户暂停通知'),
]

Receive_State = [
    ('draft', u'草稿'),
    ('confirmed', u'确认'),
    ('w_info',u'用户单'),
    ('w_price',u'报价单'),
    ('w_so',u'合同'),
    ('w_change', u'待更改'),
    ('done', u'完成'),
    ('cancel',u'作废')]

Receive_Business_State = [
    ('draft', u'草稿'),
    ('done', u'完成'),
    ('cancel',u'作废'),
]


class receive_order(osv.osv):
    _name = "receive.order"

    def _compute_file_url(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for o in self.browse(cr, uid, ids, context=context):
            res[o.id] = '%s/%s' % (o.file_path or '', o.file_name)
        return res

    _columns = {
        'name': fields.char(u'接单', size=32, readonly=True, states={'draft': [('readonly', False), ]} ),
        'partner_id': fields.many2one('res.partner', u'客户', required=True, domain=[('customer', '=', True)], readonly=True, states={'draft': [('readonly', False), ]}),
        'email_code': fields.char(u'邮件编号',size=24),

        ##Business  info
        'qty': fields.integer(u'数量',),
        'delivery_period': fields.integer(u'交付周期'),

        'state': fields.selection(Receive_State, u'状态'),
        'b_state': fields.selection(Receive_Business_State, u'商务信息状态'),

        'ref': fields.char(u'零件号', size=64, required=False, readonly=True,states={'draft': [('readonly', False), ]}, ),  # 零件号

        #TODO: binary filed can not sotre to filesystem,may be change it to a only_create m2o(ir.attachment) field,and set a wizard to create it.
        'attachment': fields.binary(u'源文件', readonly=True,states={'draft': [('readonly', False), ]},),  #附件会不会有多个？TODO: how to save it as a file,not in db

        #TODO file_name file_path file_url
        'file_name': fields.char(u'源文件名', size=64, readonly=True, states={'draft': [('readonly', False), ]},),
        'file_path': fields.char(u'目录', size=64, readonly=True,states={'draft': [('readonly', False), ]},),
        'file_url': fields.function(_compute_file_url, type='char', string=u'下载地址', readonly=True),

        'info_id': fields.many2one('pcb.info', u'用户单', readonly=True,states={'draft': [('readonly', False), ]},),
        'product_id': fields.related('info_id', 'product_id', type='many2one', relation='product.product', string=u'档案号', readonly=True),
        'price_id': fields.many2one('pcb.price', u'报价单', readonly=True,),
        'sol_id': fields.related('price_id', 'sol_id', type='many2one', relaiton='sale.order.line', string=u'订单明细', readonly=True),
        'so_id': fields.related('price_id', 'so_id', type='many2one', relation='sale.order', string=u'订单', readonly=True),

        'type': fields.selection(Receive_Type, u'类型', size=16, readonly=True,states={'draft': [('readonly', False), ]},),
        'note_special': fields.text(u'特别备注'),  # 特别备注
        'note': fields.text(u'备注'),  # 备注
        'priority': fields.selection([(1, u'高'), (10, u'低')], u'优先级', type="integer", readonly=True,states={'draft': [('readonly', False), ]},),  # 紧急


        'create_date': fields.datetime(u'创建日期', readonly=1, ),  # 创建日期
        'create_uid': fields.many2one('res.users', u'创建人', readonly=1),  # 接单记录创建人

        'approve_uid': fields.many2one('res.users', u'审核人', readonly=True,),
        'approve_date': fields.datetime(u'审核日期', readonly=1, ),
        #'f_state': fields.function(''), used to trace for  pcbinfo, pcbprice, pcborder

        'change_order_id': fields.many2one('change.order', u'更改单', readonly=True),
    }

    _defaults = {
        'name': lambda self, cr, uid, ctx: self.pool.get('ir.sequence').get(cr, uid, 'receive.order'),
        'state': 'draft',
        'b_state': 'draft',
        'recast_type': 'new',
        'priority': 10,
    }

    def confirm_b(self, cr, uid, ids, context=None):
        #check qty , delivery date
        self.write(cr, uid, ids, {'b_state': 'done'})
        return True

    def make_change_order(self, cr, uid, ids, context=None):
        #TODO 生成更改单
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if not default.get('name'):
            default.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'receive.order')})
        return super(receive_order, self).copy( cr, uid, id, default=default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for data in self.read(cr, uid, ids, ['state']):
            if data['state'] not in  ['draft', 'cancel']:
                raise osv.except_osv(_('Error'), _(u"非草稿、取消状态不可删除"))
        return super(receive_order, self).unlink(cr, uid, ids, context=context)

    def to_next(self, cr, uid, ids, context=None):
        o = self.browse(cr, uid, ids[0], context=context)
        next_order = o.change_order_id or o.so_id or o.price_id or o.info_id
        return {
            'type': 'ir.actions.act_window',
            'name': u'订单',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': next_order._name,
            'res_id':next_order.id,
        }

    def confirm(self, cr, uid, ids, context=None):
        #TODO: do some check
        self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
        return True

    def action_approve(self, cr, uid, ids, context=None):
        rec_order = self.browse(cr, uid, ids[0], context=context)
        type = rec_order.type
        if type == 'new':
            self.to_info(cr, uid, ids, context=context, rec_order=rec_order)
        elif type == 'recast':
            self.to_price(cr, uid, ids, context=context, rec_order=rec_order)
        elif type == 'change_recast':
            pass #TODO
        elif type in ['info_change', 'global_change', 'online_change', 'recast_change']:
            self.to_change_order(cr, uid, ids, context=context, rec_order=rec_order)
        return True

    def to_draft(self, cr, uid, ids, context=None):
            self.write(cr, uid, ids, {'state': 'draft'}, context=context)
            return True

    def to_info(self, cr, uid, ids, context=None, rec_order=None):
        rec_order = rec_order or  self.browse(cr, uid, ids[0], context=context)
        info_id = self.create_pcb_info(cr, uid, rec_order, context=context)
        return self.write(cr, uid, rec_order.id, {'info_id': info_id, 'state': 'w_info'}, context=context)

    def to_price(self, cr, uid, ids, context=None, rec_order=None):
        rec_order = rec_order or self.browse(cr, uid, ids[0], context=context)
        price_id = self.create_pcb_price(cr, uid, rec_order, context=context)
        return self.write(cr, uid, rec_order.id, {'price_id': price_id, 'state': 'w_price'}, context=context)

    def to_change_order(self, cr, uid, ids, context=None, rec_order=None):
        rec_order = rec_order or self.browse(cr, uid, ids[0], context=context)
        change_id = self.create_change_order(cr, uid, rec_order, context=context)
        return self.write(cr, uid, rec_order.id, {'change_order_id': change_id, 'state': 'w_change'}, context=context)

    def to_sale_order(self, cr, uid, ids, context=None,):
        so_id = self.create_sale_order(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'so_id': so_id, 'state': 'w_so'}, context=context)

    def to_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'}, context=context)
        return True

    def on_change_partner(self, cr, uid, ids, partner_id, context=None):
        if partner_id:
            user_id = self.pool.get('res.partner').read(cr, uid, partner_id, ['user_id',], context=context, load='_classic_write')['user_id']
            return {'value': {'user_id': user_id}}

    def create_pcb_info(self, cr, uid, rec_order, context=None):
        info_obj = self.pool.get('pcb.info')
        info_id = info_obj.create(cr, uid, {
            'receive_id': rec_order.id,
        }, context=context)
        return info_id

    def create_pcb_price(self, cr, uid, rec_order, context=None):
        price_obj = self.pool.get('pcb.price')
        price_ids = []
        price_id = price_obj.create(cr, uid, {
            'receive_id': rec_order.id,
            'qty': rec_order.qty,
        }, context=context)
        return price_id

    def create_change_order(self, cr, uid, rec_order, context=None):
        change_obj = self.pool.get('change.order')

        change_id = change_obj.create(cr, uid, {
            'receive_id': rec_order.id,
        }, context=context)

        return change_id

    def create_sale_order(self, cr, uid, ids, context=None, rec_orders=None,):
        so_obj = self.pool.get('sale.order')
        sol_obj = self.pool.get('sale.order.line')
        rec_orders = rec_orders or self.browse(cr, uid, ids, context=context)
        prices = [x.price_id for x in rec_orders]
        so_id = so_obj.create(cr, uid, self._prepare_sale_order(cr, uid, prices,), context=context)
        self._make_order_line(cr, uid, so_id, prices, context=context)
        return so_id

    def _prepare_sale_order(self, cr, uid, prices, context=None):
        return {
            'partner_id': prices[0].partner_id.id,
        }

    def _make_order_line(self, cr, uid, so_id, prices, context=None):
        sol_obj = self.pool.get('sale.order.line')
        price_obj = self.pool.get('pcb.price')

        once_fee_pdt_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mtlcs_sale', 'pcb_fee_once')[1]
        once_fee_pdt = self.pool['product.product'].browse(cr, uid, once_fee_pdt_id, context=context)
        sol_ids = []
        for p in prices:
            sol_id = sol_obj.create(cr, uid, {
                'name': p.name,
                'order_id': so_id,
                'price_id': p.id,
                'product_id': p.product_id.id,
                'product_uom_qty': p.qty,
                'product_uom': p.product_id.uom_id.id,
            })
            price_obj.write(cr, uid, p.id, {'sol_id': sol_id}, context=context)
            #add once_fee_line
            if p.once_fee:
                sol_obj.create(cr, uid, {
                    'name': p.name,
                    'order_id': so_id,
                    'price_id': p.id,
                    'product_id': once_fee_pdt_id,
                    'product_uom_qty': 1,
                    'product_uom':once_fee_pdt.uom_id.id,
                    'price_unit': p.once_fee,
                })
        return True
